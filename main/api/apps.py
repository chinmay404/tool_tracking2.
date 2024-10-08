from django.apps import AppConfig
import threading
import time
import schedule
import json
import os
import requests
import logging 
from main.settings import API_CALLS, API_CALLS_TIME

logger = logging.getLogger(__name__)

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    is_thread_started = False

    def ready(self):
        if API_CALLS:
            try:
                if not self.is_thread_started:
                    logger.info('[API THREADS STARTING ...]')
                    print('[API THREADS STARTING ...]')
                    threading.Thread(target=self.schedule_api_tasks, daemon=True).start()
                    self.is_thread_started = True  
                    logger.info('[API THREADS ONLINE ...]')
                    print("[API THREADS ONLINE ]")
                else:
                    logger.info('[ ! AREADY STARTED] THREADS ALREADY STARTED...')
                    print('[ ! AREADY STARTED] THREADS ALREADY STARTED...')
            except Exception as e:
                logger.error(f'[API THREADING EXCEPTION]: {e}')
            self.is_thread_started = False
    def schedule_api_tasks(self):
        while True:
            try:
                # Run parsing GRN task
                logger.info('[API] GRN API CALL ...')
                # self.schedule_parsing_grn_file()       #USE THIS FOR API CALLS FROM FILE
                self.schedule_parsing_grn()

                # Sleep for specified time
                # logger.info(f'[API] Sleep Time: {API_CALLS_TIME} Seconds')
                time.sleep(10)

                # Run sale order task
                logger.info('[API] Sale Order API REQUEST ...')
                self.schedule_sale_order()

                # Sleep for specified time
                logger.info(f'[API] Sleep Time: {API_CALLS_TIME} Seconds')
                time.sleep(10)

            except Exception as e:
                logger.error(f'[API] API Tasks Exception: {e}')
    def schedule_parsing_grn_file(self):
        from api.grn_api import parse_and_store_product_data

        file_path = '/home/sirius/Public/Tool_Tracking/main/api/grn_response.json' 
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            logger.error(f'[API] JSON file not found at: {file_path}')
            return

        parse_and_store_product_data(data,logger)

    def schedule_parsing_grn(self):
        from api.grn_api import parse_and_store_product_data

        url = 'http://10.10.1.18:8400/api/matservices/gettoolgrnlist'
        mock_server_local_url = "http://127.0.0.1:8400/api/matservices/gettoolgrnlist"
        response = requests.get(url)
        if response.status_code == 200:
            # logger.info(f'[API] GRN API RESPONSE STATUS CODE: {response.status_code}')
            data = response.json()
            if data:
                parse_and_store_product_data(data,logger)
            else:
                logger.warning('[API] RESPONSE BLANK')
        else:
            logger.error(f'[API] GRN API STATUS CODE: {response.status_code}\n Call Failed Due To Wrong Response Code.')

    def schedule_sale_order(self):
        from api.sale_order_api import create_sale_order

        url = 'http://10.10.1.18:8400/api/matservices/getsaleapilist'
        response = requests.get(url)
        # logger.info(f'[API] SALE ORDER API RESPONSE STATUS CODE: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            if data:
                create_sale_order(data)
            else:
                logger.warning('[API] RESPONSE BLANK')
        else:
            logger.error(f'[API] SALE ORDER API STATUS CODE: {response.status_code}\n Call Failed Due To Wrong Response Code.')

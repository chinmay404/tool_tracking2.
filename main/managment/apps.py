from django.apps import AppConfig
import threading
import time
import schedule
import json
import os
import requests
from main.settings import API_CALLS, API_CALLS_TIME


class ManagmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'managment'

    
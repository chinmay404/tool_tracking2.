from flask import Flask, jsonify

app = Flask(__name__)

grn_data =[
    {
        "CompanyShortName": "HTECH",
        "GrnNo": "102242540411040853",
        "GrnDate": "26/04/2024",
        "PartyName": "ALFA TOOLINGS",
        "PartyChallanNo": "107",
        "PartyChallanDate": "20240425",
        "GateInwardNo": None,
        "PoNo": "2425-000137",
        "PoDate": "05/04/2024",
        "SubGlAcNo": 1011201019,
        "ItemSummary": [
            {
                "MaterialCode": 1011324863,
                "MaterialName": "SPL COMB SEME FINISH BORING BAR DIA 79.5X1.5X15° GPL-280 BT-50 AT-A-2215 NORD BEVEL HOUSING",
                "MaterialUom": "LTR",
                "ChallanQty": 500.000,
                "ReceivedQty": 500.000,
                "StockGroupType": 101
            },
            {
                "MaterialCode": 1011324866,
                "MaterialName": "SPL OD ROUGHING BORING BAR OF DIA 181X0.5X15°CHEMFER (UNDER CUTT R0.4X1 DEEP)GPL-135 BT-50 AT-A-2218 NORD BEVEL HOUSING",
                "MaterialUom": "NOS",
                "ChallanQty": 1.000,
                "ReceivedQty": 1.000,
                "StockGroupType": 101
            },
            {
                "MaterialCode": 1011324857,
                "MaterialName": "SPL ROUGHING BORING BAR DIA 225.0 GPL-170.0 BT-50 AT-A-2209 NORD BEVEL HOUSING",
                "MaterialUom": "NOS",
                "ChallanQty": 1.000,
                "ReceivedQty": 1.000,
                "StockGroupType": 101
            },
            {
                "MaterialCode": 1011324868,
                "MaterialName": "SPL ROUGHING BORING BAR OF DIA 135 GPL-150.0 BT-50 AT-A-2220 NORD BEVEL HOUSING",
                "MaterialUom": "KGS",
                "ChallanQty": 500.000,
                "ReceivedQty": 500.000,
                "StockGroupType": 101
            }
        ]
    }
]

so_data = 

@app.route('/api/matservices/gettoolgrnlist', methods=['GET'])
def get_grn_list():
    print("CaLLED SERVER REPOSNE SENT")
    return jsonify(grn_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8400)  # Port 8400 to match your code

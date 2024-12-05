from flask import Flask, jsonify

app = Flask(__name__)

so_data = [
    {
        "OrderNo": "102232490113020699",
        "OrderDate": "24/02/2024",
        "CustomerName": "E. D. STEELS PVT LTD",
        "PartyPoNo": "004712",
        "PartyPoDate": "17/02/2024",
        "CompanyShortName": "HTECH",
        "ItemSummary": [
            {
                "MaterialName": "SPL OD ROUGHING BORING BAR OF DIA 181X0.5X15°CHEMFER (UNDER CUTT R0.4X1 DEEP)GPL-135 BT-50 AT-A-2218 NORD BEVEL HOUSING",
                "MaterialUom": "NOS",
                "PoQty": 20.000
            }
        ]
    },
    {
        "OrderNo": "102232490113020715",
        "OrderDate": "25/02/2024",
        "CustomerName": "E. D. STEELS PVT LTD",
        "PartyPoNo": "004880",
        "PartyPoDate": "08/02/2024",
        "CompanyShortName": "HTECH",
        "ItemSummary": [
            {
                "MaterialName": "SPL ROUGHING BORING BAR OF DIA 135 GPL-150.0 BT-50 AT-A-2220 NORD BEVEL HOUSING",
                "MaterialUom": "KGS",
                "PoQty": 10.000
            },
            {
                "MaterialName": "SPL COMB SEME FINISH BORING BAR DIA 79.5X1.5X15° GPL-280 BT-50 AT-A-2215 NORD BEVEL HOUSING",
                "MaterialUom": "LTR",
                "PoQty": 5.000
            }
        ]
    },
    {
        "OrderNo": "102232490113020718",
        "OrderDate": "25/02/2024",
        "CustomerName": "E. D. STEELS PVT LTD",
        "PartyPoNo": "010081",
        "PartyPoDate": "07/02/2024",
        "CompanyShortName": "HTECH",
        "ItemSummary": [
            {
                "MaterialName": "CT PORT TOOL DIA34XDIA34.3XDIA 46XFL60XOAL120XSH32 JD",
                "MaterialUom": "NOS",
                "PoQty": 3.000
            }
        ]
    }]


grn_data = [
    {
        "CompanyShortName": "HTECH",
        "GrnNo": "102242540411040153",
        "GrnDate": "26/04/2024",
        "PartyName": "ALFA TOOLINGS",
        "PartyChallanNo": "107",
        "PartyChallanDate": "20240125",
        "GateInwardNo": None,
        "PoNo": "2425-000137",
        "PoDate": "05/04/2024",
        "SubGlAcNo": 1011201019,
        "ItemSummary": [
            {
                "MaterialCode": 1011324863,
                "MaterialName": "SP",
                "MaterialUom": "LTR",
                "ChallanQty": 500.000,
                "ReceivedQty": 500.000,
                "StockGroupType": 102
            },
            {
                "MaterialCode": 1011324866,
                "MaterialName": "HOUSING",
                "MaterialUom": "NOS",
                "ChallanQty": 10.000,
                "ReceivedQty": 10.000,
                "StockGroupType": 101
            },

        ]
    }
]

# so_data =


@app.route('/api/matservices/gettoolgrnlist', methods=['GET'])
def get_grn_list():
    print("CaLLED SERVER REPOSNE SENT")
    return jsonify(grn_data), 200

# /api/matservices/getsaleapilist


@app.route('/api/matservices/getsaleapilist', methods=['GET'])
def get_so():
    print("so SENT")
    return jsonify(so_data), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8400)  # Port 8400 to match your code

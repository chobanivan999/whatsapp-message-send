from flask import Flask, request
from twilio.rest import Client
import requests
import json
from bs4 import BeautifulSoup
import mysql.connector
from flask_cors import CORS

# Configuring Twilio Credentials and Logging in
account_sid = 'ACc732f5a72960c592f6af8bf4a2bc34ab'
auth_token = 'a9c43f4aa6865352ad485336976a48ed'

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "<!doctype html><html><head><title>WhatsApp Messaging App</title></head><body><h1>WhatsApp Messaging App is Running!</h1></body></html>"

@app.route('/send', methods=['POST'])
def send():
    try:
        client = Client(account_sid, auth_token)
        msg = request.values.get('Body', '')
        phones = request.values.get('To', '')
        phones = phones.split(",")
        for phone in phones:
            res = client.messages.create(
                from_ = 'whatsapp:+601119083609',
                body = msg,
                to = 'whatsapp:' + phone
            )
        return "sent"
    except Exception as e:
        print(phone, str(e))
        return str(e)


@app.route('/banks', methods=['GET'])
def banks():
    res = {}
    try:
        # Connect DB
        mydb = mysql.connector.connect(
        host="helper-mortgage-app-server.mysql.database.azure.com",
        user="vwyqarxcyy",
        password="2UDN1QS88XH71VJK$",
        database="helper-mortgage-option-db"
        # host="localhost",
        # user="root",
        # password="",
        # database="helper-mortgage-option"
        )
        mycursor = mydb.cursor()

        mycursor.execute("SELECT COUNT(*) FROM banks WHERE STR_TO_DATE(created_at, '%Y-%m-%d') >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)")

        myresult = mycursor.fetchall()

        if myresult[0][0] == 0:
            # Clear table
            mycursor.execute("DELETE FROM banks")
            mydb.commit()
            # Scraping
            URL = "https://mortgage.redbrick.sg/package_list/icecube"
            page = requests.get(URL)

            soup = BeautifulSoup(page.content, "html.parser")
            rows = soup.findAll(True, {"class":["row row-content"]})
            if len(rows):
                rows = rows[1:51]

            banklogos = {
                'mbb': 'https://www.maybank.com/iwov-resources/images/icons/maybank_logo.svg',
                'ocbc': 'https://www.ocbc.com/iwov-resources/sg/ocbc/gbc/img/logo_ocbc.png',
                'dbs': 'https://www.dbs.com/iwov-resources/flp/images/dbs_logo.svg',
                'hsbc': 'https://www.hsbc.com/-/files/hsbc/header/hsbc-logo-200x25.svg?h=25&la=en-GB&hash=EFB19274CD17649AE659D3351B595180',
                'citibank': 'https://www.citi.com/CBOL/IA/Angular/assets/citiredesign.svg',
                'scb': 'https://av.sc.com/corp-en/nr/content/images/sc-lock-up-english-rgb-thumbnail-750x422.jpg',
                'cimb': 'https://www.cimbbank.com.ph/content/dam/cimbph/images/global/logo-cimb-islamic.svg',
                'boc': 'https://www.boc.cn/en/images/bankofchina_LOGO.gif',
                'hlf': 'https://www.hlf.com.sg/assets/images/home/logo.png',
                'Singapura-Finance': 'https://www.singapurafinance.com.sg/img/logo.png',
                'sbi': 'https://sbi.co.in/o/SBI-Theme/images/custom/logo.png',
                'uob': 'https://www.uob.com.sg/assets/iwov-resources/assets/BrandAssets/UOB_Logo.svg',
                'rhb': 'https://www.rhbgroup.com/images/global/logo-mobile_default.png'
            }
            banknames = {
                'mbb': 'Maybank',
                'ocbc': 'OCBC',
                'dbs': 'DBS',
                'hsbc': 'HSBC',
                'citibank': 'Citibank',
                'scb': 'Standard Chartered',
                'cimb': 'CIMB Bank',
                'boc': 'Bank of China',
                'hlf': 'Hong Leong Finance',
                'Singapura-Finance': 'Singapura Finance Ltd',
                'sbi': 'State Bank of India',
                'uob': 'UOB',
                'rhb': 'RHB'
            }

            for row in rows:
                bankkey = row.img['src'].split("/")[-1].split(".")[0]
                name = banknames[bankkey]
                img = banklogos[bankkey]
                ratetype = row.find(True, {"class":["package-type"]}).text.strip()
                lockin = row.find(True, {"class":["package-lockin"]}).text.strip()
                rate = row.find(True, {"class":["package-rate"]}).text.strip().split("\n")
                rate = '<br>'.join([item.strip() for item in rate if item != "Interest Rate"])
                installment = row.find(True, {"class":["box__instalment"]}).text.strip().split("\n")
                installment = '<br>'.join([item.strip() for item in installment if item != "Monthly Instalments"])
                content = {
                        "ratetype": ratetype,
                        "lockin": lockin,
                        "rate": rate,
                        "installment": installment
                    }
                mycursor.execute("SELECT name, image, content FROM banks WHERE name=%s AND image=%s AND content=%s", (name, img, json.dumps(content)))
                myresult = mycursor.fetchall()
                if len(myresult) == 0:
                    mycursor.execute("INSERT INTO banks (name, image, content) VALUES (%s, %s, %s)", (name, img, json.dumps(content)))
            mydb.commit()

        mycursor.execute("SELECT name, image, content FROM banks")
        myresult = mycursor.fetchall()
        mydb.close()
        
        res["status"] = "success"
        res["data"] = list(myresult)
        return res
    except Exception as e:
        res["status"] = "fail"
        res["data"] = str(e)
        return res

if __name__ == '__main__':
    app.run()
from flask import Flask, request
from twilio.rest import Client
from flask_cors import CORS

# Configuring Twilio Credentials and Logging in
account_sid = 'ACc732f5a72960c592f6af8bf4a2bc34ab'
auth_token = 'a9c43f4aa6865352ad485336976a48ed'
client = Client(account_sid, auth_token)

app = Flask(__name__)
CORS(app)

@app.route('/send', methods=['POST'])
def send():
    msg = request.values.get('Body', '')
    phones = request.values.get('To', '')
    phones = phones.split(",")
    print(phones)
    for phone in phones:
        message = client.messages.create(
            from_ = 'whatsapp:+601119083609',
            body = msg,
            to = 'whatsapp:' + phone
        )

    return "success"

if __name__ == '__main__':
    app.run()
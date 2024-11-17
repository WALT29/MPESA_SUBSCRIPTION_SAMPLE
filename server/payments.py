import base64
import requests
from datetime import datetime
from flask import Blueprint,request,make_response
from flask_restful import Api,Resource
from dotenv import load_dotenv
import os


load_dotenv()

mpesa_bp=Blueprint('mpesa_bp',__name__,url_prefix='/mpesa')
api=Api(mpesa_bp)


consumer_key=os.getenv('Consumer_key')
consumer_secret_key=os.getenv('Consumer_secret')

#token
def authorization(url):
    #Base64 encode consumer_key and consumer_secret_key
    plain_text=f'{consumer_key}:{consumer_secret_key}'
    bytes_obj=bytes(plain_text,'utf-8')
    bs4=base64.b64encode(bytes_obj)
    bs4str=bs4.decode()
    headers={
        'Authorization':'Basic ' + bs4str
    }
    res=requests.get(url,headers=headers)
    return res.json().get('access_token')

def generate_timestamp():
    time = datetime.now().strftime('%Y%m%d%H%M%S')
    return time

def create_password(shortcode,passkey,timestamp):
    plain_text = shortcode+passkey+timestamp
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)
    bs4 = bs4.decode()
    return bs4


def format_phone_number(number):
    number_str=str(number)
    if number_str.startswith('07'):
        return int('254' + number_str[1:])
    
    elif number_str.startswith('254'):
        return int(number_str)
    else:
        return None

class Payment(Resource):
    def post(self):
        data=request.get_json()
        number=data['number']
        amount=data['amount']
        
        if not amount or not str(amount).isdigit() or int(amount) <=0:
            return make_response(
                {
                    "error":"Please enter a valid amount and the value should be greater than zero"
                },400
            )
        
        formatted_phone_number=format_phone_number(number)
        time=generate_timestamp()
        password=create_password("174379","bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",time)
        
        payload = {
            "BusinessShortCode": 174379,
            "Password": password,
            "Timestamp": time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": 254790453418,
            "PartyB": 174379,
            "PhoneNumber": formatted_phone_number,
            "CallBackURL": "https://major-aardvark-secondly.ngrok-free.app/payment_result",
            "AccountReference": "Medrin",
            "TransactionDesc": "Payment of X"
         } 
        
        token = authorization('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials')
        headers = {'Authorization': 'Bearer '+token}
        res = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers=headers, json=payload)
        response_data=res.json()
        return response_data,res.status_code



class Payment_result(Resource):
    def post(self):
        print("Callback received:", request.json)
        return make_response({"status": "Callback received"}, 200)






api.add_resource(Payment,'/make_payment')   
api.add_resource(Payment_result,'/payment_result')        
    

        
        
    

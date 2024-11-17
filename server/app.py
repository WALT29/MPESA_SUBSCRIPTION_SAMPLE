from datetime import datetime
from flask import Flask,request,make_response
from flask_cors import CORS
from flask_restful import Api,Resource
from models import db,Subscription,User,Payments,Plans,Jobs
from payments import mpesa_bp




app=Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
app.register_blueprint(mpesa_bp)

api=Api(app)



db.init_app(app)




    
if __name__ == '__main__':
    app.run(port=5555,debug=True)
        
        
    

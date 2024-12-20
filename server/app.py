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

#############################################################################USER RESOURCE#############################################################################
class Users(Resource):
    def get(self):
        users=[user.to_dict() for user in User.query.all()]
        
        if not users:
            return make_response(
                {
                    "error":"No users found"
                },400
            )
        
        return make_response(users,200)
    
    def post(self):
        data=request.get_json()
        name=data['name']
        phone_number=data['phone_number']
        password=data['password']
            
        errors=[]
        if len(name)<2:
            errors.append("Name is required and name should be at least 3 characters")
        if not phone_number.isdigit() or not len(phone_number) ==10:
            errors.append('Phone number should be 10 characters and have digits only')
        if len(password) <8 :
            errors.append('Password should be at least 8 characters')
        
        user =User.get_by_phonenumber(number=phone_number)
        
        if user is not None:
            errors.append("User with that Number exists")
        
        if errors:
            return make_response({
                "errors":errors
            },400)
            
        new_user=User(name=name,
                      phone_number=phone_number,
                      )
        
        new_user.set_password(password=password)
        new_user.save()
        
        return make_response(new_user.to_dict(),201)
        
api.add_resource(Users,'/users')

class Users_by_id(Resource):
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        
        if not user:
            return make_response(
                {
                    "error":"No user with that id is found"
                },400
            )
        
        return make_response(user.to_dict(),200)

api.add_resource(Users_by_id,'/users/<int:id>') 
            
################################ PLANS RESOURCE ##########################################################
class Plan(Resource):
    def get(self):
        plans=[plan.to_dict() for plan in Plans.query.all()]
        
        if  not plans:
            return make_response(
                {
                    "error":"No plans are found"
                },400
            )
        
        return make_response(plans,200)
    
    def post(self):
        data=request.get_json()
        name=data['name']
        description=data['description']
        cost=data['cost']
        job_limit=data.get('job_limit',None)
        duration_days=data.get('duration_days',None)
        
        
        errors=[]
        if not name or not isinstance(name,str):
            errors.append("Enter the name of the plan")
            
        if not description or not isinstance(description,str):
            errors.append("Enter description and description must be a string")
        
        try:
            cost = float(cost) 
            if cost < 0:
                errors.append("Cost must be greater or equal to zero")
        except ValueError:
            errors.append("Enter a valid cost value, it must be a number")
        
        if errors:
            return make_response(
                {
                    "error":errors
                },400
            )
        
        new_plan=Plans(name=name,cost=cost,description=description,job_limit=job_limit,duration_days=duration_days)
        db.session.add(new_plan)
        db.session.commit()
        
        return make_response(new_plan.to_dict(),201)
api.add_resource(Plan,'/plans')

################################################ SUBSCRIPTION RESOURCE #############################################
class Subscriptions(Resource):
    def get(self):
        subscriptions=[subscription.to_dict() for subscription in Subscription.query.all()]
        if not subscriptions:
            return make_response({
                "error":"No subscriptions found"
            },404)
        
        return make_response(subscriptions,200)
    
    
    def post(self):
        data=request.get_json()
        user_id=data['user_id']
        plan_id=data['plan_id']
        #here i validate payment if the payment is a success
        payment=Payments.query.filter_by(user_id=user_id,plan_id=plan_id,payment_status='success').first()
        
        if not payment:
            return make_response({"error": "No successful payment found for this plan"}, 400)
        
        #here i check if the user has an active subscription
        active_subscription=Subscription.query.filter_by(user_id=user_id, plan_id=plan_id).first()
        
        if active_subscription and active_subscription.is_active():
            return make_response({"error": "User already has an active subscription for this plan"}, 400)
        
        # After i check that the user has no active subscription ,I add a new subscription
        new_sub = Subscription(user_id=user_id, plan_Id=plan_id)
        db.session.add(new_sub)
        db.session.commit()        
        return make_response(new_sub.to_dict(),201)
    

    
if __name__ == '__main__':
    app.run(port=5555,debug=True)
        
        
    

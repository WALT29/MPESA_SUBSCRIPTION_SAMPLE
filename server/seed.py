from models import db,Subscription,User,Payments,Plans,Jobs
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()
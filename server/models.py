from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone,timedelta

metadata=MetaData()
db=SQLAlchemy(metadata=metadata)

class User(db.Model,SerializerMixin):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    phone_number=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)
    
    jobs=db.relationship('Jobs',back_populates='user',cascades='all delete-orphan')
    subscriptions=db.relationship('Subscription',back_populates='users',cascades='all delete-orphan')
    plans=association_proxy('subscriptions','Plan',creator=lambda plan_obj:Subscription(plan=plan_obj))
    
    payments=db.relationship('Payments',back_populates='user')
    
    serialize_rules=('payments.user','jobs.users','plans.users')
    

class Plans(db.Model,SerializerMixin):
    __tablename__='plans'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False) # free ,silver ,gold
    cost=db.Column(db.Float,nullable=False,default=0.0)
    job_limit=db.Column(db.Integer,nullable=True) #Null for unlimited days 
    duration_days=db.Column(db.Integer,nullable=True)
    
    subscriptions=db.relationship('Subscription',back_populates='plans',cascades='all delete-orphan')
    users=association_proxy('subscriptions','User',creator=lambda user_obj:Subscription(user=user_obj))
    
    serialize_rules=('-subscriptions','users.plans')

class Subscription(db.Model,SerializerMixin):
    __tablename__='company_subscription'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    plan_id=db.Column(db.Integer,db.ForeignKey('plans.id'),nullable=False)
    start_date=db.Column(db.DateTime,default=lambda:datetime.now(timezone(timedelta(hours=3))))
    end_date=db.Column(db.DateTime ,nullable=True)
    
    user=db.relationship('User',back_populates='subscriptions')
    plan=db.relationship('Plans',back_populates='subscriptions')
    
    serialize_rules=('-user','-plan')
    
    
    def __init__(self,user_id,plan_Id):
        self.user_id=user_id
        self.plan_id=plan_Id
        self.start_date=datetime.now(timezone(timedelta(hours=3)))
        
        
        plan=Plans.query.get(plan_Id)
        
        if plan.duration_days>0:
            self.end_date=self.start_date + timedelta(days=plan.duration_days)
        
    def is_active(self):
        if self.end_date:
            return datetime.now(timezone(timedelta(hours=3))) <= self.end_date
        return True
    
    def remaining_jobs(self):
        if self.plan.job_limit is not None:
            return self.plan.job_limit-len(self.user.jobs)
        
class Jobs(db.Model,SerializerMixin):
    __tablename__='company_subscription'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String,nullabe=False)
    description=db.Column(db.Text,nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone(timedelta(hours=3))))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    
    users=db.relationship('User',back_populates='jobs')
    
    serialize_rules=('users.jobs',)
    
class Payments(db.Model):
    __tablename__='payments'
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Float,nullable=False)
    phone_number=db.Column(db.string,nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=3))))
    transaction_reference = db.Column(db.String, nullable=False, unique=True)
    
    plan_id=db.Column(db.Integer,db.ForeignKey('plans.id'))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    
    user = db.relationship('User', back_populates='payments')
    plan = db.relationship('Plans', back_populates='payments')
    serialize_rules = ('-user', '-plan.payments')
    
    

from main import app
from user import db, User
from job import Job
from application import Application
from subscription import Subscription

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

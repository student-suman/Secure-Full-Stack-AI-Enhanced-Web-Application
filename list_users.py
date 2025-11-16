from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    if not users:
        print("Database has no users.")
    else:
        print("--- Users in Database ---")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}")
        print("-------------------------")
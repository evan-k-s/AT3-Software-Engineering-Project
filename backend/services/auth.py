from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import User, db
import re
import html

def login_user(username, password):
    user = User.query.filter_by(username=username).first()

    if not user or not user.verify_password(password):
        raise AccessError("Invalid email or password")
    
    session_token, csrf_token = user.initiate_user_session()

    return session_token, csrf_token
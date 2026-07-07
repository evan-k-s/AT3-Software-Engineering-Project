from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import User, db, UserProfile
from datetime import datetime
import re
import html

def auth_login_user(username, password):
    user = User.query.filter_by(username=username).first()

    if not user or not user.verify_password(password):
        raise AccessError("Invalid email or password")
    
    session_token, csrf_token = user.initiate_user_session()

    return session_token, csrf_token, user


def auth_register_user(username, email, password):

    email = str(email).strip()
    valid_email = bool(re.match("^([^.@ ]+(?:.[^.@ ]+)@[^.@ ]+\.[^.@ ]+[\.\w]+).{1,}$", email))
    if not valid_email:
        raise InputError("Invalid email!")
    
    email = email.lower()
    exists = User.query.filter_by(email=email).first() is not None
    if exists:
        raise InputError("Email already exists!")

    sanitised_email = html.escape(email)

    sanitised_password = html.escape(str(password))
    sanitised_password = sanitised_password.replace("&amp", "&")


    valid_password = bool(re.match("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", str(password)))

    if not valid_password:
        raise InputError("Invalid password: must be alphanumeric, contain special characters, and be 8-20 characters long")
    
    malicious_words = [
        "onerror",
        "javascript:",
        "onload",
        "onclick",
        "onmouseover",
        "onfocus",
        "\x00"
    ]

    for word in malicious_words:
        if re.search(word, str(username)):
            username = str(username).replace(word, "")

    sanitised_username = html.escape(str(username))

    if type(username) == str:
        valid_username = bool(re.match("^[^ ]+(?:\s[^ ]+)*$", username))
    else:
        valid_username = False

    if (not valid_username) or (len(str(username)) > 70):
        raise InputError("Invalid name!")
    
    user_created_time = datetime.now()

    new_user_instance = User(sanitised_username, sanitised_email, user_created_time, sanitised_password)

    session_token, csrf_token = new_user_instance.initiate_user_session()
    
    new_user_instance.save_to_db()

    new_user_details = UserProfile(new_user_instance, False, None, None, None)

    new_user_details.save_to_db()

    return session_token, csrf_token

def auth_logout_user(session_token):
    user = User.query.filter_by(session_token=session_token).first()

    if user:
        user.revoke_user_session()
from classes.Error import InputError, AccessError
from database.data import User, db

def authorise_user(session_token, csrf_token):
    """Authorises user IFF a valid session token exsist"""
    # Check whether tokens are valid tokens found in user sessions
    token = User.query.filter_by(session_token=session_token).first() is not None
    print(token)
    if (User.query.filter_by(session_token=session_token).first() is not None) and (User.query.filter_by(csrf_token=csrf_token).first() is not None):
        return True
    else:
        raise AccessError("Invalid Session Token or CSRF Token")


def map_session_token_to_email(target_session_token):
    """func mapping the session token to registered user email"""
    user = User.query.filter_by(session_token=target_session_token).first()
    if user is not None:
            return user.email
    else:
        raise InputError(f"Session token '{target_session_token}' not found")
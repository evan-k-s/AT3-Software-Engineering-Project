from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from database.data import db, User
import re
import os


# Specify alternative location for templates
TEMPLATE_DIR = os.path.abspath('../frontend')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=TEMPLATE_DIR)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load local .env file
load_dotenv()

# Credentials from .env for MySQL db
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

# Configure MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@localhost/{db_name}"
db.init_app(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    data = request.form
    if request.method == 'POST':
        if "username" in data and "password" in data:
            username = data["username"]
            password = data["password"]
            return render_template('index.html', msg='Logged in successfully!')
        else:
            msg = "Missing required fields: username and password"
    
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    return render_template('register.html', msg=msg)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
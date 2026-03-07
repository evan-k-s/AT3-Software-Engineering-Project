from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS
import re
import os


TEMPLATE_DIR = os.path.abspath('../frontend')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=TEMPLATE_DIR)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
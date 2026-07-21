# AT3-Software-Engineering-Project Book Reviewing Web App


## Overview

My Book Reviewing Web App is a web app designed to allow users to review any books they have read, whether it was their favourite, or not for them. The user can then generate recommendations for what to read next based on how they have reviewed past books. The purpose of this application is to address one of the major barriers to deciding to pick up a book rather than pick up a phone. By helping users find what they enjoy, the application aims to give reading the same simplicity as choosing to scroll.

---

## Prerequisites

### Python 3

Ensure you have Python 3 installed:

```bash
python3 --version
```

If not installed, download from [python.org](https://www.python.org/downloads/) or use your system's package manager.


### MySQL

Ensure you have MySQL installed:
```bash
mysql --version
```

If not installed, follow the instuctions for your system from [dev.mysql.com](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/).

Once installed start the server on your system using system settings (Mac) and verify it is running.

```bash
mysql -u root -p
```

Enter the password and create the database for this system called books-webapp-db and verify it has been successfully created

```bash
CREATE DATABASE books-webapp-db;
SHOW DATABASES;
```

---

## Manual Setup Guide

### Step 1: Clone the Repository

```bash
$ git clone https://github.com/evan-k-s/AT3-Software-Engineering-Project
```

### Step 2: Open in VSCode

Open the cloned repository in VSCode

### Step 3: Install Packages

```bash
cd backend
pip3 install -r ../requirements.txt
```


## Execute App

### Run Backend

1. Navigate to backend folder:

```bash
$ cd backend
```

2. Start the server:

```bash
$ python3 app.py
```

3. The backend will run at:

```
http://127.0.0.1:5000
```

Open this URL in your browser

---

## Project Structure
```
project/
|
├– README.md                  # This file – setup instructions
├– requirements.txt           # Required packages
|
├– backend/                   # Python Flask API
|  ├– app.py                  # Main Flask application entry point
|  ├– classes/                # Data structures
|  |  └– Error.py             # Custom exception classes
|  ├– core/                   # Business logic layer
|  |  └– auth_core.py         # Authentication logic
|  ├– database/               # Database structures
|  |  └– data.py              # Database tables and functions
|  ├– decorators/             # Custom decorators
|  |  └– error.py             # Custom error functionality
|  ├– services/               # API route handlers
|  |  ├– auth.py              # Handles authentication functionality
|  |  ├– recommendations.py   # Handles recommendations functionality
|  |  └– review.py            # Handles reviews functionality
└– frontend/                  # Plain HTML, CSS, JS frontend
   ├– src/
   |  ├– assets/              # Fonts and SVG assets
   |  ├– scripts/             # JS script logic
   |  ├– services/            # API calls
   |  |  ├– api.js            # Connection to fetch backend
   |  |  ├– auth.js           # Auth API calls
   |  |  ├– logout.js         # Logout API calls
   |  |  ├– recommendation.js # Recommendations API calls
   |  |  └– review.js         # Reviews API calls
   |  └– styles/              # CSS styles
   └–  templates/             # HTML templates
```

---

Hope you enjoy this project! 

~Evan

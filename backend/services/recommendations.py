from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import db, Review, User
from datetime import datetime
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load local .env file
load_dotenv()

# Configure OpenAI API
openai_api_key = os.environ['OPENAI_API_KEY']
openai_model = os.environ['OPENAI_MODEL']
openai_endpoint = os.environ['OPENAI_ENDPOINT']

client = OpenAI(
    base_url=openai_endpoint,
    api_key=openai_api_key,
)

class BookPreferences(BaseModel):
    liked_genres: list[str]
    disliked_genres: list[str]
    liked_authors: list[str]
    disliked_authors: list[str]
    liked_eras: list[str]
    disliked_eras: list[str]

def find_user_preferences(reviews_text):
    prompt = f"""Analyse the following set of a single user's book reviews and ratings. Extract their liked and 
    disliked: genres, authors, and eras (as in era of literature NOT era of the setting). Prioritise explicit
    preferences, but also look for implicit preferences within the review body for each book.
    
    Reviews: 
    {reviews_text}"""

    try:
        response = client.chat.completions.parse(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system", "content": "You are a helpful literary expert. Help the user understand their book preferences"
                },
                {
                    "role": "user", "content": prompt
                }
            ],
            response_format=BookPreferences
        )
        preferences = response.choices[0].message.parsed
        
        return preferences
    except:
        raise AccessError("Error extracting reviews")
import requests
from flask_sqlalchemy import SQLAlchemy
from classes.Error import InputError, AccessError
from database.data import db, Review, User, RecentRecommendation, SavedRecommendation, UserProfile
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
    disliked: genres, authors, and eras (as in era of literature NOT era of the setting - the era should be returned 
    as a range i.e. 1950 TO 1960). Prioritise explicit preferences, but also look for implicit preferences within the 
    review body for each book.
    
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


def find_book_recommendations(preferences, user, no_author=False, limit=12):
    if (not preferences.liked_genres) and (not preferences.liked_authors) and (not preferences.liked_eras):
        raise AccessError("Preferences cannot be extracted! Please increase the detail of your review bodies.")
    
    base_url = "https://openlibrary.org/search.json"

    query_params = []

    user_details = UserProfile.query.filter_by(user_id=user.id).first()

    if preferences.liked_genres:
        genres = " OR ".join(preferences.liked_genres)
        genres_string = f"subject:({genres})"
        query_params.append(genres_string)
        user_details.update(liked_genres=preferences.liked_genres)
    
    if preferences.liked_authors and not no_author:
        authors = " OR ".join(preferences.liked_authors)
        authors_string = f"author:({authors})"
        query_params.append(authors_string)
        user_details.update(liked_authors=preferences.liked_authors)
    
    if preferences.liked_eras:
        eras = []
        for era in preferences.liked_eras:
            if "TO" in era:
                eras.append(f"[{era}]")
            else:
                eras.append(era)
        eras_string = " OR ".join(eras)
        query_params.append(eras_string)
        user_details.update(liked_eras=preferences.liked_eras)
    
    query_string = " AND ".join(query_params)

    full_url = f"{base_url}?q={query_string}&limit={limit}"

    print(full_url)

    response = requests.get(full_url)

    data = response.json()

    books = data['docs']

    return books


def store_recent_recommendations(books, user, combine_recs=False):
    has_recents = user.recent_recommendations is not None

    if has_recents and not combine_recs:
        RecentRecommendation.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    recs_num = 0
    
    for book in books:
        if book.get('cover_edition_key') is None:
            continue

        title = book['title']
        author = ", ".join(book['author_name'])
        olid = book['cover_edition_key']
        published = book['first_publish_year']
        created_at = datetime.now()

        if User.query.join(User.reviews).filter(User.id==user.id, Review.olid==olid).first() is not None:
            continue

        recent_recommendation = RecentRecommendation(user, title, author, olid, published, created_at)

        recent_recommendation.save_to_db()

        recs_num += 1

    return recs_num


def user_save_recommendation(recommendation_id, user):
    recent_recommendation = RecentRecommendation.query.filter_by(id=recommendation_id).first()

    if recent_recommendation is not None:
        title = recent_recommendation.title
        author = recent_recommendation.author
        olid = recent_recommendation.olid
        published = recent_recommendation.published
        saved_at = datetime.now()

        exists = User.query.join(User.saved_recommendations).filter(User.id==user.id, SavedRecommendation.olid==olid).first() is not None

        if exists:
            raise AccessError("Already saved!")

        saved_recommendation = SavedRecommendation(user, title, author, olid, published, saved_at)

        saved_recommendation.save_to_db()


def user_delete_recommendation(user, id):
    recommendation = SavedRecommendation.query.filter_by(user_id=user.id, id=id).first()
    db.session.delete(recommendation)
    db.session.commit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from google_play_scraper import app, reviews, Sort
from transformers import pipeline
import re
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import uuid  # For generating unique table names

# Function to extract app ID from the app's URL
def extract_app_id(url):
    return url.split('=')[-1]

# Function to perform sentiment analysis using DistilBERT
def analyze_sentiment(text):
    # Specifying the Hugging Face model name and revision
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    revision = "af0f99b"

    # Load the sentiment analysis pipeline with the specified model and revision
    classifier = pipeline("sentiment-analysis", model=model_name, revision=revision)

    results = classifier(text)
    label = results[0]['label']
    score = results[0]['score']
    return label, score

# Function to clean text
def clean_text(text):
    if text is None:
        return ""
    # Lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    return text

# Function to extract emojis
def extract_emojis(text):
    emojis = re.findall(r'[^\w\s,]', text)
    return ''.join(emojis)

# Function to create a new table to store reviews
def create_reviews_table(engine, table_suffix):
    Base = declarative_base()

    # Define a model for the reviews table
    class Review(Base):
        __tablename__ = f'reviews_{table_suffix}'  # Use a unique table name
        id = Column(Integer, Sequence('review_id_seq'), primary_key=True)
        review = Column(String)
        sentiment_label = Column(String)
        sentiment_score = Column(Float)
        created_at = Column(DateTime, default=datetime.datetime.now)

    print(f"Created Table: {Review.__tablename__}")

    # Create the reviews table if it doesn't exist
    Base.metadata.create_all(engine)

    return Review

# Function to scrape and save reviews to the database
def scrape_and_save_reviews(app_id, num_reviews, session, Review):
    review_result, _ = reviews(
        app_id,
        lang='en',
        country='us',
        sort=Sort.MOST_RELEVANT,
        count=num_reviews,
    )
    progress_bar = tqdm(total=num_reviews, desc="Scraping Reviews", position=0)

    unique_reviews = []
    positive_reviews = 0
    total_reviews = 0

    for review_count, review in enumerate(review_result, start=1):
        review_text = review['content']

        # Clean the review text
        cleaned_text = clean_text(review_text)
        if not cleaned_text:
            continue  # Skip empty reviews

        if cleaned_text not in unique_reviews:
            sentiment_label, sentiment_score = analyze_sentiment(cleaned_text)
            if sentiment_label == "POSITIVE":
                positive_reviews += 1
            total_reviews += 1

            # Create a Review record and add it to the database
            new_review = Review(review=cleaned_text, sentiment_label=sentiment_label, sentiment_score=sentiment_score)
            session.add(new_review)
            session.commit()

            unique_reviews.append(cleaned_text)

        # Update the progress bar
        progress_bar.update(1)

    progress_bar.close()

    positive_percentage = (positive_reviews / total_reviews) * 100
    print(f"Positive Review Percentage: {positive_percentage:.2f}%")

    return positive_percentage  # Return positive percentage 

# Main function to control the entire process
def main(search_query, num_reviews=100, table_suffix=None):
    # Create a Chrome webdriver
    driver = webdriver.Chrome()
    driver.get("https://play.google.com/store")

    # Find the search icon by class and aria-hidden attribute
    search_icon = driver.find_element(By.CSS_SELECTOR, '.google-material-icons[aria-hidden="true"]')
    search_icon.click()

    # Wait for the search input to become visible
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Search Google Play"]')
    while not search_input.is_displayed():
        time.sleep(1)

    # Enter the user-provided search query
    search_input.send_keys(search_query + Keys.RETURN)
    time.sleep(5)

    # Find the link in the specified div
    link = driver.find_element(By.CSS_SELECTOR, '.Qfxief')

    # Get the app URL
    app_url = link.get_attribute("href")
    app_id = extract_app_id(app_url)
    link.click()
    time.sleep(5)
    see_more_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="See more information on Ratings and reviews"]')
    see_more_button.click()

    # Scroll down to load reviews
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Define PostgreSQL database connection URL
    db_url = "postgresql://postgres:12345@localhost/reviews"

    # Generate a unique table name (e.g., based on a UUID)
    table_suffix = str(uuid.uuid4())
    print(f"Main Function - Table Name: reviews_{table_suffix}")

    # Create a SQLAlchemy engine and session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    # Create a new table to store reviews
    Review = create_reviews_table(engine, table_suffix)

    # Print the name of the created table
    print(f"Main Function - Created Table: {Review.__tablename__}")

    # Create a session for database operations
    session = Session()

    # Scrape and save reviews to the database
    positive_percentage  = scrape_and_save_reviews(app_id, num_reviews, session, Review)

    # Close the database session
    session.close()

    driver.quit()
    
    return positive_percentage, None, f"{Review.__tablename__}"

if __name__ == '__main__':
    main("your_search_query", num_reviews=100)

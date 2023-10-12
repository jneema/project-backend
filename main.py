import json
import pandas as pd
import re
import emoji
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from textblob import TextBlob
from sqlalchemy import create_engine, MetaData, Table, Column, Float, String, inspect
from sqlalchemy.exc import IntegrityError
from google_play_scraper import app, Sort, reviews

# PostgreSQL database configuration
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/api"  

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

# Function to perform sentiment analysis
def sentiment_analysis(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Function to calculate positive review percentage
def calculate_positive_percentage(df):
    positive_reviews = df[df['sentiment_score'] > 0]
    percentage_positive = (len(positive_reviews) / len(df)) * 100
    return percentage_positive

# # Scrape reviews for multiple apps with aliases
# app_data = [
#     {'alias': 'Betika', 'package_name': 'pl.loyaltyclub.betika'},
#     {'alias': 'Betting App Kenya', 'package_name': 'ke.co.ipandasoft.premiumtipsfree'},
#     {'alias': 'Odi Bets', 'package_name': 'com.odibet.app'},
#     {'alias': 'Sport Pesa', 'package_name': 'sportpesa.app3'}
# ]

# # Scrape reviews for multiple apps with aliases
# app_data = [
#     {'alias': 'M-Pesa app', 'package_name': 'com.safaricom.mpesa.lifestyle'},
#     {'alias': 'Safaricom app', 'package_name': 'com.safaricom.mysafaricom'},
#     {'alias': 'Airtel App', 'package_name': 'com.airtel.africa.selfcare'},
#     {'alias': 'Telkom', 'package_name': 'com.mytelkom'},
#     {'alias': 'T-kash', 'package_name': 'com.tkashapp'}
# ]

# # Scrape reviews for multiple apps with aliases
# app_data = [
#     {'alias': 'Tala', 'package_name': 'com.inventureaccess.safarirahisi'},
#     {'alias': 'Zenka', 'package_name': 'com.zenkafinance.microloans'},
#     {'alias': 'Branch', 'package_name': 'com.branch_international.branch.branch_demo_android'},
#     {'alias': 'Okash', 'package_name': 'com.loan.cash.credit.okash.nigeria'},
# ]

# Scrape reviews for multiple apps with aliases
app_data = [
    {'alias': 'Standard Chartered', 'package_name': 'com.scb.breezebanking.ke'},
    {'alias': 'Equity', 'package_name': 'ke.co.equitygroup.equitymobile'},
    {'alias': 'Absa', 'package_name': 'com.absa.ke.mobile.android.ui'},
    {'alias': 'KCB', 'package_name': 'com.kcbbankgroup.android'},
    {'alias': 'Vooma', 'package_name': 'com.kcbbankgroup.vooma.android'},
    {'alias': 'Stanbic', 'package_name': 'com.cfcstanbicbank.app'},
    {'alias': 'NCBA', 'package_name': 'com.nicbank.android'},
    {'alias': 'I&M', 'package_name': 'com.imbank.digital.retail.app'},
    {'alias': 'Consolidated', 'package_name': 'com.bank.myconso'},
    {'alias': 'MCO-OPCASH', 'package_name': 'com.mcoopcash.retail'},
    {'alias': 'PesaPap,Family Bank', 'package_name': 'com.mode.familykenya.ui'},
    {'alias': 'Kenya Baroda Mobi', 'package_name': 'com.barodakenya'},
    {'alias': 'Access Bank', 'package_name': 'com.craftsilicon.transnationalbank'},

]

# Create a SQLAlchemy engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the table structure for new and combined data
table_structure_new = Table(
    'banking_apps',
    metadata,
    Column('Alias', String, primary_key=True),
    Column('Positive_Review_Percentage', Float)
)

table_structure_combined = Table(
    'all_reviews',
    metadata,
    Column('Alias', String, primary_key=True),
    Column('Positive_Review_Percentage', Float)
)

# Check if the tables already exist in the database
inspector = inspect(engine)

# Create tables if they don't exist
if not inspector.has_table('banking_apps'):
    metadata.create_all(engine)
    print("banking_apps table created")

if not inspector.has_table('all_reviews'):
    metadata.create_all(engine)

# Create a connection to the database
with engine.connect() as conn:
    for app_info in app_data:
        package_name = app_info['package_name']
        result, _ = reviews(
            package_name,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=5000
        )
        
        df = pd.DataFrame(result)
        df['cleaned_content'] = df['content'].apply(clean_text)
        df['extracted_emojis'] = df['cleaned_content'].apply(extract_emojis)
        df['sentiment_score'] = df['cleaned_content'].apply(sentiment_analysis)
        
        # Calculate and store the positive review percentage along with the alias
        percentage_positive = calculate_positive_percentage(df)
        alias = app_info['alias']
        
        # Insert data into the new table
        try:
            conn.execute(table_structure_new.insert().values(Alias=alias, Positive_Review_Percentage=percentage_positive))
            print(f"Inserted data for {alias} into new table")
        except IntegrityError as e:
            # Handle duplicate entry errors, if any
            print(f"Error inserting data for {alias} into new table: {e}")
            
        # Insert data into the combined table
        try:
            conn.execute(table_structure_combined.insert().values(Alias=alias, Positive_Review_Percentage=percentage_positive))
            print(f"Inserted data for {alias} into combined table")
        except IntegrityError as e:
            # Handle duplicate entry errors, if any
            print(f"Error inserting data for {alias} into combined table: {e}")

        conn.commit()
# Close the database connection
engine.dispose()

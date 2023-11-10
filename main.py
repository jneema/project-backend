from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from scraper import main
import uuid  # For generating a unique table suffix

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str
    numReviews: int

class ScrapeResponse(BaseModel):
    message: str
    positive_review_percentage: float

@app.post("/scrape_reviews/")
async def scrape_reviews(search_query: SearchQuery):
    query = search_query.query
    num_reviews = search_query.numReviews

    # Generate a unique table name suffix for this request
    table_suffix = str(uuid.uuid4())

    # Call the scraping function with the table suffix
    success = main(query, num_reviews, table_suffix)

    if success:
        return ScrapeResponse(message="Scraping completed successfully", positive_review_percentage=0.0)
    else:
        return ScrapeResponse(message="Scraping failed", positive_review_percentage=0.0)

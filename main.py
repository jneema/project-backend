from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import main
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the latest table name
latest_table_name = None

class SearchQuery(BaseModel):
    query: str
    numReviews: int

class ScrapeResponse(BaseModel):
    message: str
    positive_review_percentage: float
    table_name: str

@app.post("/scrape_reviews/")
async def scrape_reviews(search_query: SearchQuery):
    global latest_table_name  # Declare the global variable

    query = search_query.query
    num_reviews = search_query.numReviews

    # Call the scraping function without generating a new table name
    positive_percentage, table_data, table_name = main(query, num_reviews)

    # Update the global variable with the latest table name
    latest_table_name = table_name

    return ScrapeResponse(
        message="Scraping completed successfully",
        positive_review_percentage=positive_percentage,
        table_name=table_name,
    )

@app.get("/get_latest_table_data/")
async def get_latest_table_data():
    global latest_table_name  # Retrieve the latest table name
    # print(latest_table_name)

    if latest_table_name is None:
        return {"message": "No table data available."}
    
    table_name_with_prefix = f"{latest_table_name}"

    db_url = "postgresql://postgres:12345@localhost/reviews"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    metadata = MetaData()
    latest_table = Table(table_name_with_prefix, metadata, autoload_with=engine)
    result = session.query(latest_table).all()

    session.close()

    table_data = [{"id": row.id, "review": row.review, "sentiment_label": row.sentiment_label, "sentiment_score": row.sentiment_score, "created_at": row.created_at} for row in result]

    return {"table_name": table_name_with_prefix, "table_data": table_data}

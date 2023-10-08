from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table, select
from fastapi.middleware.cors import CORSMiddleware


# Create a FastAPI app instance
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL database configuration
DATABASE_URL = "postgresql://postgres:12345@localhost/api"  

# Create a SQLAlchemy engine and metadata
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Defining the table structure for all reviews
table_structure_all_reviews = Table(
    'all_reviews',
    metadata,
    autoload=True,
    autoload_with=engine
)

table_structure_betting_apps = Table(
    'betting_apps',
    metadata,
    autoload=True,
    autoload_with=engine
)

table_structure_loan_apps = Table(
    'loan_apps',
    metadata,
    autoload=True,
    autoload_with=engine
)

table_structure_mobile_banking = Table(
    'mobile_banking',
    metadata,
    autoload=True,
    autoload_with=engine
)

# Define a Pydantic model to represent the data
from pydantic import BaseModel

class ReviewItem(BaseModel):
    Alias: str
    Positive_Review_Percentage: float

# API route to get all review items
@app.get("/allreviews", response_model=list[ReviewItem])
async def all_reviews():
    query = select([table_structure_all_reviews])
    result = []
    with engine.connect() as conn:
        rows = conn.execute(query)
        for row in rows:
            result.append(ReviewItem(Alias=row['Alias'], Positive_Review_Percentage=row['Positive_Review_Percentage']))
    return result

# API route to get items from the betting apps table
@app.get("/bettingapps", response_model=list[ReviewItem])
async def betting_apps():
    query = select([table_structure_betting_apps])
    result = []
    with engine.connect() as conn:
        rows = conn.execute(query)
        for row in rows:
            result.append(ReviewItem(Alias=row['Alias'], Positive_Review_Percentage=row['Positive_Review_Percentage']))
    return result

# API route to get items from the loan apps table
@app.get("/loanapps", response_model=list[ReviewItem])
async def loan_apps():
    query = select([table_structure_loan_apps])
    result = []
    with engine.connect() as conn:
        rows = conn.execute(query)
        for row in rows:
            result.append(ReviewItem(Alias=row['Alias'], Positive_Review_Percentage=row['Positive_Review_Percentage']))
    return result

# API route to get items from the mobile banking table
@app.get("/mobilebanking", response_model=list[ReviewItem])
async def mobile_banking():
    query = select([table_structure_mobile_banking])
    result = []
    with engine.connect() as conn:
        rows = conn.execute(query)
        for row in rows:
            result.append(ReviewItem(Alias=row['Alias'], Positive_Review_Percentage=row['Positive_Review_Percentage']))
    return result

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

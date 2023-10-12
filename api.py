from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI
from typing import Generator, List
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine("postgresql://postgres:12345@localhost:5432/api")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

conn = SessionLocal()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define SQLAlchemy models
class ReviewItem(Base):
    __tablename__ = "banking_apps"  

    Alias = Column(String, primary_key=True, index=True)
    Positive_Review_Percentage = Column(Float)

class AllReview(Base):
    __tablename__ = "all_reviews"
    Alias = Column(String, primary_key=True)
    Positive_Review_Percentage = Column(Float)

class LoanApp(Base):
    __tablename__ = "loan_apps"
    Alias = Column(String, primary_key=True)
    Positive_Review_Percentage = Column(Float)

class BettingApp(Base):
    __tablename__ = "betting_apps"
    Alias = Column(String, primary_key=True)
    Positive_Review_Percentage = Column(Float)

class Telecommunication(Base):
    __tablename__ = "telecommunications"
    Alias = Column(String, primary_key=True)
    Positive_Review_Percentage = Column(Float)


class FeedbackDB(Base):
    __tablename__ = "feedback"

    name = Column(String, primary_key=True, index=True)
    text = Column(String)
    rating = Column(Integer)

# Pydantic model for the response
class ReviewItemResponse(BaseModel):
    Alias: str
    Positive_Review_Percentage: float

class FeedbackCreate(BaseModel):
    name: str
    text: str
    rating: int

class FeedbackResponse(BaseModel):
    name: str
    text: str
    rating: int

# In your route handler, use the SQLAlchemy model to query the data
@app.get("/bankingapps", response_model=List[ReviewItemResponse])
async def banking_apps(db: Session = Depends(get_db)):
    items = db.query(ReviewItem).all()
    return items

# API route to get items from the 'all_reviews' table
@app.get("/allreviews", response_model=List[ReviewItemResponse])
async def get_all_reviews(db: Session = Depends(get_db)):
    return db.query(AllReview).all()

# API route to get items from the 'loan_apps' table
@app.get("/loanapps", response_model=List[ReviewItemResponse])
async def get_loan_apps(db: Session = Depends(get_db)):
    return db.query(LoanApp).all()

# API route to get items from the 'betting_apps' table
@app.get("/bettingapps", response_model=List[ReviewItemResponse])
async def get_betting_apps(db: Session = Depends(get_db)):
    return db.query(BettingApp).all()

# API route to get items from the 'telecommunications' table
@app.get("/telecommunications", response_model=List[ReviewItemResponse])
async def get_telecommunication(db: Session = Depends(get_db)):
    return db.query(Telecommunication).all()

@app.post("/feedback/")
async def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = FeedbackDB(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# API route to get items from the 'feedbsck' table
@app.get("/allfeedback", response_model=List[FeedbackResponse])
async def get_feedback(db: Session = Depends(get_db)):
    feedback_items = db.query(FeedbackDB).all()
    return feedback_items
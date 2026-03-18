from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uvicorn

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    portfolios = relationship("Portfolio", back_populates="owner")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_value = Column(Float)
    owner = relationship("User", back_populates="portfolios")
    assets = relationship("Asset", back_populates="portfolio")

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    symbol = Column(String)
    quantity = Column(Float)
    current_price = Column(Float)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio", back_populates="assets")

# Create tables
Base.metadata.create_all(bind=engine)

# Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Seed data
from sqlalchemy.orm import Session

def seed_data(db: Session):
    if not db.query(User).first():
        user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
        db.add(user)
        db.commit()
        db.refresh(user)

        portfolio = Portfolio(user_id=user.id, total_value=1000.0)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

        asset = Asset(name="Bitcoin", symbol="BTC", quantity=0.1, current_price=50000.0, portfolio_id=portfolio.id)
        db.add(asset)
        db.commit()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api-docs", response_class=HTMLResponse)
async def read_api_docs(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def read_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/api/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    user = db.query(User).first()  # Simplified for demo
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    return portfolio

@app.post("/api/transactions")
async def add_transaction():
    return {"message": "Transaction added"}

@app.get("/api/market-data")
async def get_market_data():
    return {"data": "Real-time market data"}

if __name__ == "__main__":
    with SessionLocal() as db:
        seed_data(db)
    uvicorn.run(app, host="0.0.0.0", port=8000)

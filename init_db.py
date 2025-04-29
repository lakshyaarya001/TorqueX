from app import create_app, db
from app.models import User, CarListing, PricePrediction

app = create_app()

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    # Create all tables with the current schema
    db.create_all()
    print("Database initialized successfully!")

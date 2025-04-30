import pandas as pd

# Load the car dataset
df = pd.read_csv('cleaned_car.csv')
brands = sorted(df['Brand'].unique())
models = sorted(df['model'].unique())

def get_models_for_brand(brand):
    """Get all models for a given brand"""
    return sorted(df[df['Brand'] == brand]['model'].unique()) 
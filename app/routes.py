from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, CarListingForm, PricePredictionForm
from app.models import User, CarListing, PricePrediction
from app.car_data import df, brands, get_models_for_brand
import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

main = Blueprint('main', __name__)

# Load or train the price prediction model
model_path = 'car_price_model.joblib'
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    # Prepare data for training
    X = df[['Year', 'Age', 'kmDriven']]
    y = df['Price']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_path)

@main.route("/")
@main.route("/home")
def home():
    car_listings = CarListing.query.filter_by(is_sold=False).all()
    return render_template('home.html', car_listings=car_listings)

@main.route("/cars")
def display_cars():
    url = "https://car-data.p.rapidapi.com/cars"
    
    querystring = {"limit": "30", "page": "0"}
    
    headers = {
        "x-rapidapi-key": "6f49b92699msh582e9b70b299e68p1028f6jsn4a593ab49eb4", 
        "x-rapidapi-host": "car-data.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    print(response.status_code)
    print(response.text)

    if response.status_code == 200:
        car_data = response.json()
    else:
        car_data = []
    

    return render_template('display.html', cars=car_data)

@main.route("/car/<int:car_id>")
def car_detail(car_id):
    car = CarListing.query.get_or_404(car_id)
    return render_template('car_details.html', car=car)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_seller=form.is_seller.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_seller:
        car_listings = CarListing.query.filter_by(seller_id=current_user.id).all()
        return render_template('seller_dashboard.html', car_listings=car_listings)
    else:
        car_listings = CarListing.query.filter_by(is_sold=False).all()
        return render_template('buyer_dashboard.html', car_listings=car_listings)

@main.route('/list_car', methods=['GET', 'POST'])
@login_required
def list_car():
    if not current_user.is_seller:
        flash('You need to be a seller to list cars', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CarListingForm()
    
    if form.validate_on_submit():
        # Validate model against brand
        from app.car_data import get_models_for_brand
        valid_models = get_models_for_brand(form.brand.data)
        if form.model.data not in valid_models:
            flash('Please select a valid model for the chosen brand', 'danger')
            return render_template('list_car.html', title='List Car', form=form)
        
        car = CarListing(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            mileage=form.mileage.data,
            transmission=form.transmission.data,
            owner=form.owner.data,
            fuel_type=form.fuel_type.data,
            price=form.price.data,
            description=form.description.data,
            image_url=form.image_url.data,
            seller_id=current_user.id
        )
        db.session.add(car)
        db.session.commit()
        flash('Car listed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('list_car.html', title='List Car', form=form)

@main.route('/predict_price', methods=['GET', 'POST'])
def predict_price():
    form = PricePredictionForm()
    form.brand.choices = [(brand, brand) for brand in brands]
    form.model.choices = [(model, model) for model in get_models_for_brand(form.brand.data)]
    
    if form.validate_on_submit():
        # Prepare input data for prediction
        input_data = pd.DataFrame({
            'Age': [2024 - form.year.data],
            'kmDriven': [form.mileage.data],
            'Transmission': [1 if form.transmission.data == 'Automatic' else 0],
            'Owner': [form.owner.data],
            'FuelType': [0 if form.fuel_type.data == 'Petrol' else 1 if form.fuel_type.data == 'Diesel' else 2],
            'Brand': [form.brand.data]
        })
        
        # Create a DataFrame with all possible brand columns
        all_brands = ['Ashok', 'Aston Martin', 'Audi', 'BMW', 'Bajaj', 'Bentley', 'Chevrolet', 
                     'Citroen', 'Datsun', 'Fiat', 'Force', 'Ford', 'Honda', 'Hummer', 'Hyundai', 
                     'ICML', 'Isuzu', 'Jaguar', 'Jeep', 'Kia', 'Lamborghini', 'Land Rover', 
                     'Lexus', 'MG', 'Mahindra', 'Maruti Suzuki', 'Maserati', 'Mercedes-Benz', 
                     'Mini', 'Mitsubishi', 'Nissan', 'Opel', 'Porsche', 'Renault', 'Rolls-Royce', 
                     'Skoda', 'Ssangyong', 'Tata', 'Toyota', 'Toyota Land', 'Volkswagen', 'Volvo']
        
        # Create a DataFrame with all possible brand columns initialized to 0
        brand_columns = pd.DataFrame(0, index=[0], columns=[f'Brand_{brand}' for brand in all_brands])
        
        # Set the selected brand to 1
        selected_brand = f'Brand_{form.brand.data}'
        if selected_brand in brand_columns.columns:
            brand_columns[selected_brand] = 1
        
        # Create owner column
        owner_column = pd.DataFrame({'Owner_second': [1 if form.owner.data == 'Second' else 0]})
        
        # Combine all features
        input_data_encoded = pd.concat([
            input_data[['Age', 'kmDriven', 'Transmission', 'FuelType']],
            brand_columns,
            owner_column
        ], axis=1)
        
        # Load the trained model
        model = joblib.load('app/car_price_predictor.pkl')
        
        # Make prediction
        predicted_price = model.predict(input_data_encoded)[0]
        
        # Save prediction to database
        prediction = PricePrediction(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            mileage=form.mileage.data,
            transmission=form.transmission.data,
            owner=form.owner.data,
            fuel_type=form.fuel_type.data,
            predicted_price=predicted_price
        )
        db.session.add(prediction)
        db.session.commit()
        
        return render_template('prediction_result.html', 
                             predicted_price=predicted_price,
                             form=form)
    
    return render_template('predict_price.html', title='Predict Price', form=form)

@main.route('/get_models/<brand>')
def get_models(brand):
    # Filter models for the selected brand
    models = get_models_for_brand(brand)
    return jsonify(models)

@main.route('/mark_sold/<int:car_id>', methods=['POST'])
@login_required
def mark_sold(car_id):
    car = CarListing.query.get_or_404(car_id)
    if car.seller_id != current_user.id:
        flash('You are not authorized to mark this car as sold', 'danger')
        return redirect(url_for('main.dashboard'))
    car.is_sold = True
    db.session.commit()
    flash('Car marked as sold successfully!', 'success')
    return redirect(url_for('main.dashboard'))

from flask import Blueprint, render_template, url_for, flash, redirect
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Car
import requests

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

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

@main.route("/cars")
def car_list():
    cars = Car.query.all()  
    return render_template('car_list.html', cars=cars)

@main.route("/car/<int:car_id>")
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('car_detail.html', car=car)

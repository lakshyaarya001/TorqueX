from flask import Blueprint, render_template, url_for, flash, redirect
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Car

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Handle login logic here
        pass
    return render_template('login.html', form=form)

@main.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Handle signup logic here
        pass
    return render_template('signup.html', form=form)

@main.route("/cars")
def car_list():
    cars = Car.query.all()  # Assuming Car is a model in models.py
    return render_template('car_list.html', cars=cars)

@main.route("/car/<int:car_id>")
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('car_detail.html', car=car)

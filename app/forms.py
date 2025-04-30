from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_seller = BooleanField('Register as a Seller')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CarListingForm(FlaskForm):
    brand = SelectField('Brand', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    mileage = FloatField('Mileage (km)', validators=[DataRequired()])
    transmission = SelectField('Transmission', choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')], validators=[DataRequired()])
    owner = SelectField('Owner', choices=[('first', 'First'), ('second', 'Second'), ('third', 'Third'), ('fourth', 'Fourth')], validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric')], validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description')
    image_url = StringField('Image URL')
    submit = SubmitField('List Car')

    def __init__(self, *args, **kwargs):
        super(CarListingForm, self).__init__(*args, **kwargs)
        from app.car_data import brands
        self.brand.choices = [(brand, brand) for brand in brands]

    def validate_model(self, model):
        if self.brand.data:
            from app.car_data import get_models_for_brand
            valid_models = get_models_for_brand(self.brand.data)
            if model.data not in valid_models:
                raise ValidationError('Please select a valid model for this brand')

class PricePredictionForm(FlaskForm):
    brand = SelectField('Brand', validators=[DataRequired()])
    model = SelectField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1990, max=2024)])
    mileage = IntegerField('Mileage (km)', validators=[DataRequired(), NumberRange(min=0)])
    transmission = SelectField('Transmission', choices=[('Automatic', 'Automatic'), ('Manual', 'Manual')], validators=[DataRequired()])
    owner = SelectField('Owner', choices=[('First', 'First'), ('Second', 'Second'), ('Third', 'Third'), ('Fourth & Above', 'Fourth & Above')], validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('CNG', 'CNG')], validators=[DataRequired()])
    submit = SubmitField('Predict Price')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class CheckoutForm(FlaskForm):
    # Billing Information
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])

    # Shipping Address
    address = StringField("Street Address", validators=[DataRequired(), Length(min=5, max=200)])
    city = StringField("City", validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=50)])
    zip_code = StringField("ZIP Code", validators=[DataRequired(), Length(min=5, max=10)])
    country = SelectField("Country", choices=[('US', 'United States'), ('CA', 'Canada')],
                          validators=[DataRequired()])

    # Payment Information
    card_number = StringField("Card Number", validators=[DataRequired(), Length(min=13, max=19)])
    expiry_month = SelectField("Expiry Month",
                               choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
                               validators=[DataRequired()])
    expiry_year = SelectField("Expiry Year",
                              choices=[(str(i), str(i)) for i in range(2024, 2035)],
                              validators=[DataRequired()])
    cvv = StringField("CVV", validators=[DataRequired(), Length(min=3, max=4)])

    submit = SubmitField("Place Order")


class ProductSearchForm(FlaskForm):
    search = StringField("Search Products", validators=[Optional(), Length(max=200)])
    category = SelectField("Category", choices=[('', 'All Categories')], validators=[Optional()])
    min_price = FloatField("Min Price", validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField("Max Price", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Search")


class ContactForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Send Message")


class NewsletterForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")


class ReviewForm(FlaskForm):
    rating = SelectField("Rating", choices=[('5', '5 Stars'), ('4', '4 Stars'),
                                            ('3', '3 Stars'), ('2', '2 Stars'), ('1', '1 Star')],
                         validators=[DataRequired()])
    title = StringField("Review Title", validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField("Review Content", validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField("Submit Review")
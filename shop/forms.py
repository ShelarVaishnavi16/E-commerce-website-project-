from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, TextAreaField
from flask_wtf.file import FileAllowed, FileField, FileRequired


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()], )
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForms(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()], )
    password = PasswordField('New Password', [validators.DataRequired()])


class Addprouducts(Form):
    name = StringField('Name', [validators.DataRequired()])
    price = IntegerField('Price', [validators.DataRequired()])
    discount = IntegerField('Discount', default=0)
    stock = IntegerField('stock', [validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    colors = TextAreaField('colors', [validators.DataRequired()])

    image_1 = FileField('Image_1',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_2 = FileField('Image_2',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
    image_3 = FileField('Image_3',
                        validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])


class ContactForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35), validators.Email()], )
    phone = StringField('Contact: ', [validators.DataRequired()])
    message = TextAreaField('Description', [validators.DataRequired()])

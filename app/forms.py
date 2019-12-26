from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, DateField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email

import common
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Ваш логин:', validators=[DataRequired()])
    password = PasswordField('Введите пароль:')


class RegistrationForm(FlaskForm):
    username = StringField('Ваш логин:', validators=[DataRequired()])
    fullname = StringField('Полное имя:', validators=[DataRequired()])
    password = PasswordField('Введите пароль:')
    password2 = PasswordField('Повторите пароль:', validators=[EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Этот логин уже занят.')

    def validate_fullname(self, fullname):
        user = User.query.filter_by(fullname=fullname.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято.')


class EditAvatarForm(FlaskForm):
    image = FileField('Выбрать файл', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Формат файла должен быть .jpg или .png')
    ])


class EditProfileForm(FlaskForm):
    fullname = StringField('Полное имя:', validators=[DataRequired()])
    birthdate = DateField('Дата рождения:', validators=[DataRequired()])
    email = StringField('Почта:', validators=[DataRequired(), Email()])
    phone = StringField('Телефон:', validators=[DataRequired()])

    def __init__(self, original_fullname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_fullname = original_fullname

    def validate_fullname(self, fullname):
        user = User.query.filter_by(fullname=fullname.data).first()
        if self.original_fullname != fullname.data and user is not None:
            raise ValidationError('Это имя уже занято.')


class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль:')
    new_password = PasswordField('Новый пароль:')
    new_password2 = PasswordField('Повторите пароль:', validators=[EqualTo('new_password')])


class InputProblemForm(FlaskForm):
    source = StringField('Ответ:', validators=[DataRequired()])


class FileProblemForm(FlaskForm):
    language = SelectField(
        'Programming language',
        choices=list(common.LANGUAGE_MATCHING.items()),
        default='cpp'
    )
    source = FileField('Выберите файл', validators=[
        FileRequired()
    ])

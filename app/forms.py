from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import ValidationError, DataRequired, EqualTo
from wtforms import StringField, PasswordField, SubmitField
from wtforms_components import IntegerField, DateField, SelectField, EmailField

import constants
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Ваш логин:', validators=[DataRequired()])
    password = PasswordField('Введите пароль:')


class RegistrationForm(FlaskForm):
    username = StringField('Ваш логин:', validators=[DataRequired()])
    email = EmailField('Введите почту:', validators=[DataRequired()])
    password = PasswordField('Введите пароль:')
    password2 = PasswordField('Повторите пароль:', validators=[
        EqualTo('password', message='Пароли должны совпадать')
    ])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Этот логин уже занят.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Эта почта уже занята.')


class RestorePasswordForm(FlaskForm):
    username = StringField('Введите ваш логин:', validators=[DataRequired()])


class VerificationCodeForm(FlaskForm):
    code = StringField('Введите код:', validators=[DataRequired()])


class EditAvatarForm(FlaskForm):
    image = FileField('Выбрать файл', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Формат файла должен быть .jpg или .png')
    ])


class EditProfileForm(FlaskForm):
    first_name = StringField('Имя:')
    second_name = StringField('Фамилия:')
    email = EmailField('Почта:', validators=[DataRequired()])

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if self.original_email != email.data and user is not None:
            raise ValidationError('Эта почта уже занята.')


class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль:')
    new_password = PasswordField('Новый пароль:')
    new_password2 = PasswordField('Повторите пароль:', validators=[EqualTo('new_password')])


class InputProblemForm(FlaskForm):
    source = StringField('Ответ:', validators=[DataRequired()])


class FileProblemForm(FlaskForm):
    language = SelectField(
        'Programming language',
        choices=list(constants.LANGUAGE_MATCHING.items()),
        default='cpp'
    )
    source = FileField('Выберите файл', validators=[
        FileRequired()
    ])


class AdminInfoForm(FlaskForm):
    name = StringField('Название контеста:', validators=[DataRequired()])
    duration = IntegerField('Продолжительность (минут):', validators=[DataRequired()])
    contest_type = SelectField('Тип контеста:', choices=[('Virtual', 'Виртуальный')])

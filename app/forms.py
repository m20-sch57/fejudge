from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.validators import DataRequired


# class RestorePasswordForm(FlaskForm):
#     username = StringField('Введите ваш логин:', validators=[DataRequired()])


# class VerificationCodeForm(FlaskForm):
#     code = StringField('Введите код:', validators=[DataRequired()])


# class EditAvatarForm(FlaskForm):
#     image = FileField('Выбрать файл', validators=[
#         FileRequired(),
#         FileAllowed(['jpg', 'png'], 'Формат файла должен быть .jpg или .png')
#     ])


# class EditProfileForm(FlaskForm):
#     first_name = StringField('Имя:')
#     last_name = StringField('Фамилия:')
#     email = EmailField('Почта:', validators=[DataRequired()])

#     def __init__(self, original_email, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.original_email = original_email

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if self.original_email != email.data and user is not None:
#             raise ValidationError('Эта почта уже занята.')


# class EditPasswordForm(FlaskForm):
#     old_password = PasswordField('Старый пароль:')
#     new_password = PasswordField('Новый пароль:')
#     new_password2 = PasswordField('Повторите пароль:', validators=[
#         EqualTo('new_password', message='Пароли должны совпадать')
#     ])


# class AdminInfoForm(FlaskForm):
#     name = StringField('Название контеста:', validators=[DataRequired()])
#     contest_type = SelectField('Тип контеста:', choices=[('Virtual', 'Виртуальный')])
#     duration = IntegerField('Продолжительность (минут):', validators=[
#         DataRequired(), NumberRange(min=1, max=1000000)
#     ])

#     def __init__(self, original_name, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.original_name = original_name

#     def validate_name(self, name):
#         contest = Contest.query.filter_by(name=name.data).first()
#         if self.original_name != name.data and contest is not None:
#             raise ValidationError('Это имя уже занято.')


class UploadPackageForm(FlaskForm):
    package = FileField('Выберите файл', validators=[DataRequired()])

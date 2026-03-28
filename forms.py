from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Content", validators=[DataRequired()])
    category = SelectField("Category", coerce=int, validators=[DataRequired()])
    tags = StringField("Tags (comma-separated)")
    status = SelectField(
        "Status",
        choices=[("draft", "Draft"), ("published", "Published")],
        validators=[DataRequired()],
    )
    cover_image = FileField(
        "Cover Image",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"], "Image files only.")],
    )
    submit = SubmitField("Save Post")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class CommentForm(FlaskForm):
    author_name = StringField("Name", validators=[DataRequired(), Length(max=80)])
    author_email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    body = TextAreaField("Comment", validators=[DataRequired(), Length(min=2)])
    submit = SubmitField("Submit Comment")

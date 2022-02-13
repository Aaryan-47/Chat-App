# =============================================================================
# importing necesary libraries
# =============================================================================
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
# from flask_wtf.file import FileField, FileRequired, FileAllowed
# from wtforms.fields import FileField,FileRequired, FileAllowed
from wtforms.validators import InputRequired, Length
#  ValidationError, DataRequired
# from tables import User

 


# =============================================================================
# sign up form
# =============================================================================
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=10)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Register")

    # def validateUsername(self,username):
    #     isExisting = User.query.filter_by(username==username.data).first()
    #     if isExisting:
    #         raise ValidationError( "User already exists!!")
    

# =============================================================================
# login form
# =============================================================================
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4,max=10)], render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")



# =============================================================================
# updata status form
# =============================================================================
class searchUserForm(FlaskForm):
    userSearch = StringField(validators=[InputRequired(), Length(min=0,max=20)], render_kw={"placeholder":"Search users"})
    submit = SubmitField("Search")


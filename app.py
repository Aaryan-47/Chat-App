# =============================================================================
# importing the necessary libraries
# =============================================================================
from base64 import decode
from tkinter.messagebox import NO
from flask import Flask, render_template, url_for, redirect, request,Request, Response, session
from flask_login import login_user, LoginManager, login_required,logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
# from database import db, db_init
# from tables import User, StatusUpload, activityStack
from forms import LoginForm, RegisterForm
# from werkzeug.utils import secure_filename
from flask_session import Session
from flask_redis import FlaskRedis
# =============================================================================


# =============================================================================
# initalising the app, session and database
# =============================================================================
app = Flask(__name__)
redis_client = FlaskRedis(app,host='localhost', port=6379, db=0)
bcrypt=Bcrypt(app)
app.config['SECRET_KEY'] = "NobodyCanReadThis"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # max-limit 4MB
app.config['SESSION_TYPE'] = 'redis'
sess = Session()
sess.init_app(app)
# =============================================================================


# =============================================================================
# initalising login Manager
# =============================================================================
# loginManager = LoginManager()
# loginManager.init_app(app)
# loginManager.login_view = "login"

# @loginManager.user_loader
# def load_user(user_id):
#     print("user:", user_id)
#     return redis_client.smembers(f"user:{int(user_id)}")
# =============================================================================

# class User(UserMixin):
#   def is_active(self):
#      return True
#   def get_id(self):
#       return super().get_id()





# =============================================================================
# home page
# =============================================================================
@app.route('/')
def home():
    return render_template('index.html')

# =============================================================================
# login
# =============================================================================
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username =form.username.data
        userID=redis_client.get(username)
        if userID!=None:
            entities=redis_client.smembers(userID)
            if entities!=None:
                entities=list(entities)
                user = entities
                if user:
                    # print(type(form.password.data))
                    print(user[1])
                    print(type(user[1]))
                    if user[1].decode('UTF-8') == username:
                        i=0
                    else:
                        i=1
                    if bcrypt.check_password_hash(user[i], form.password.data):
                              print("hello")
                            #   login_user(User) 
                              session['value'] = userID
                              session[userID]=True
                              return redirect(url_for('dashboard'))
                    
        # user = User.query.filter_by(username=form.username.data).first()
    #     if user:
    #         if bcrypt.check_password_hash(user.password, form.password.data ):
    #             login_user(user) 
    #             return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

# =============================================================================
# sign up
# =============================================================================
@app.route('/signUp', methods=['GET','POST'])
def signUp():
    form = RegisterForm()
    if form.validate_on_submit():
        if (redis_client.get('total_user')==None):
            redis_client.set('total_user', 1)
        else:
            redis_client.incr('total_user')
        userId = redis_client.get('total_user')
        userId = userId.decode('UTF-8')
        print(userId)
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode("UTF-8")
        username = form.username.data
        redis_client.set(username, f"user:{userId}")
        redis_client.sadd(f"user:{userId}", username)
        redis_client.sadd(f"user:{userId}", hashedPassword)
        print(redis_client.smembers(f"user:{userId}"))
        slist = list(redis_client.smembers(f"user:{userId}"))
        slist[1] = slist[1].decode('UTF-8')
        slist[0] = slist[0].decode('UTF-8')
        print(slist)
        return redirect(url_for('login'))
    return render_template('signUp.html', form=form)

# =============================================================================
# logout
# =============================================================================
@app.route('/logout', methods=['GET','POST'])
# @login_required
def logout():
    if session.get(session.get('value'))==True:
        session[session.get('value')]=False
    session['value']=None
    # logout_user()
    return redirect(url_for('login'))

# =============================================================================
# user dashboard
# =============================================================================
@app.route('/dashboard', methods=['GET','POST'])
# @login_required
def dashboard():
    if session.get(session.get('value'))==True:
        # session[session.get('value')]=False
        return "welcome to dashboard"
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(debug=True, port=5000)


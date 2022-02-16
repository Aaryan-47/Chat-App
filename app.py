# =============================================================================
# importing the necessary libraries
# =============================================================================
from flask import Flask, render_template, url_for, redirect, request,Response, session
from flask_bcrypt import Bcrypt
from forms import LoginForm, RegisterForm, searchUserForm
from flask_session import Session
from flask_redis import FlaskRedis
import datetime
# =============================================================================


# =============================================================================
# initalising the app, session and database
# =============================================================================
app = Flask(__name__)
redis_client = FlaskRedis(app,host='localhost', port=6379, db=0)
bcrypt=Bcrypt(app)
app.config['SECRET_KEY'] = "NobodyCanReadThis"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # max-limit 4MB
app.config['SESSION_TYPE'] = 'redis'
sess = Session()
sess.init_app(app)
# =============================================================================


# =============================================================================
# yielding messages function
# =============================================================================
def event_stream(channel_number):
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(channel_number)
    # TODO: handle client disconnection.
    # print("in sub")
    for message in pubsub.listen():
        # print(message['data'])
        yield 'data: %s\n\n' % message['data'].decode('UTF-8')



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
                    if user[1].decode('UTF-8') == username:
                        i=0
                    else:
                        i=1
                    if bcrypt.check_password_hash(user[i], form.password.data):
                              session['value'] = userID
                              session[userID]=True
                              session['user'] = username
                              return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

# =============================================================================
# sign up
# =============================================================================
@app.route('/signUp', methods=['GET','POST'])
def signUp():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        if redis_client.get(username)!=None:
            return redirect(url_for('signUp'))
        if (redis_client.get('total_user')==None):
            redis_client.set('total_user', 1)
        else:
            redis_client.incr('total_user')
        userId = redis_client.get('total_user')
        userId = userId.decode('UTF-8')
        # print(userId)
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode("UTF-8")
        username = form.username.data
        redis_client.set(username, f"user:{userId}")
        # redis_client.set(f"user:{userId}user", username)
        redis_client.sadd(f"user:{userId}", username)
        redis_client.sadd(f"user:{userId}", hashedPassword)
        # print(slist)
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
    session['user'] = None
    session['value']=None
    session['activeChat'] = None
    session['activeYou'] = None
    # logout_user()
    return render_template('index.html')

# =============================================================================
# user dashboard
# =============================================================================
@app.route('/dashboard', methods=['GET','POST'])
# @login_required
def dashboard():
    # userID = session.get('value')
    if session.get(session.get('value'))==True:
        form = searchUserForm()
        if form.validate_on_submit():
            List = redis_client.scan_iter(f"*{form.userSearch.data}*")
            # print(type(userList))
            userList =[]
            for i in List:
                   string = i.decode('UTF-8')
                #    print("string:", string)
                   try:
                       checkString = redis_client.get(string).decode('UTF-8')
                    #    print("checkString:", checkString)
                       if checkString[0:4]=='user':
                           userList.append(string)
                   except:
                        pass
            try:
               userList.remove(session.get('user'))
            except:
                pass
            print(userList)
            flag=1
            return render_template('dashboard.html', form=form, userList=userList, flag=flag)
        previousChatSet = redis_client.zrange(f"{session.get('value').decode('UTF-8')}:rooms",0, -1,desc=True)
        previousChatSet= list(previousChatSet)
        previousChatList =[]
        for i in previousChatSet:
                   previousChatList.append(i.decode('UTF-8'))
        flag = 0
        return render_template('dashboard.html', form=form, previousChatList=previousChatList, flag=flag)
    return redirect(url_for('login'))





# =============================================================================
# chatroom
# =============================================================================

@app.route('/chatroom/<string:user2>')
def chatroom(user2):
    if session.get(session.get('value'))==True:
        idme= redis_client.get(session.get('user')).decode('UTF-8')[5:]
        idyou= redis_client.get(user2).decode('UTF-8')[5:]
        idme = int(idme)
        idyou= int(idyou)
        session['activeYou'] = user2
        session['activeChat'] = f"{min(idme, idyou)}:{max(idme, idyou)}"
        # print(session.get('activeChat'))
        activeChatList = redis_client.lrange(f"room:{session.get('activeChat')}", 0 , -1)
        outGoingActiveChatList =[]
        rightIndent =[]
        for i in range(len(activeChatList)):
            message = activeChatList[i].decode('UTF-8')
            if (message.find(user2)==-1):
                rightIndent.append(i)
            outGoingActiveChatList.append(message)
        # print(outGoingActiveChatList)
        return render_template('chat.html', user2=user2, activeChatList=outGoingActiveChatList, rightIndent=rightIndent)
    return redirect(url_for('login'))

# =============================================================================
# publishing messages
# =============================================================================
@app.route('/post', methods=['POST'])
def post():
    message = request.form['message']
    user = session.get('user', 'anonymous')
    # dateToday= datetime.date.today().strftime('%d-%m-%Y')
    dateTimeNow = datetime.datetime.today().strftime("%d-%m-%Y %I:%M %p")
    channel_message = '[%s] %s: %s' % (dateTimeNow, user, message)
    redis_client.publish(f"chat:{session.get('activeChat')}", channel_message)
    redis_client.rpush(f"room:{session.get('activeChat')}", channel_message)
    redis_client.zincrby(f"{session.get('value').decode('UTF-8')}:rooms", 1, session.get('activeYou'))
    redis_client.zincrby(f"{redis_client.get(session.get('activeYou')).decode('UTF-8')}:rooms", 1, session.get('user'))
    # print("got out of pub")
    return Response(status=204)

# =============================================================================
# pubsub messaging
# =============================================================================
@app.route('/stream')
def stream():
    if session.get(session.get('value'))==True:
        channel_number = f"chat:{session.get('activeChat')}"
        return Response(event_stream(channel_number), mimetype="text/event-stream")
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True, port=5000)


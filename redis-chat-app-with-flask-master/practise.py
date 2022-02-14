import redis
from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
redis_client = FlaskRedis(app,host='localhost', port=6379, db=0)
# redis.Redis(host='localhost', port=6379, db=0)



# client.set("name", "Anu")
# print(str(client.get("name"))[1:])


@app.route('/<string:keys>/<string:value>')
def set(keys, value):
    # if redis_client.exists(keys):
    #     pass
    # else:
    redis_client.set(keys, value)
        # redis_client.commit()

    return "OK"

@app.route('/get/<string:keys>')
def get(keys):
    if redis_client.exists(keys):
        return redis_client.get(keys)
    else:
        return f"{keys} doesn't exists"


app.run(port=5000, debug=True)


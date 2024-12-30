from flask_mysqldb import MySQL
import redis

mysql = MySQL()
redis_client = redis.StrictRedis(
    host="localhost",
    port=6379,
    decode_responses=True    
)
def init_db(app):
    mysql.init_app(app)    

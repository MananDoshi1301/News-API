import bcrypt
import datetime
from flask import Flask, request, jsonify
from app.database import mysql, redis_client
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import News
from app.decorators import all_news_cache

def return_error(message: str, statuscode: int):
    return jsonify({"error": message}), statuscode


def get_cursor():
    db_conn = mysql.connection.cursor()
    return db_conn

def register_routes(server: Flask):

    @server.route("/news/favourite", methods=["POST"])
    @jwt_required()
    def save_favourite():
        data = request.get_json()
        article_id = data.get("article_id", None)
        if not article_id: return_error("Missing required details", 400)        

        if not isinstance(article_id, int) and not article_id.isdigit():
            return_error("Incorrect data", 400)

        if not isinstance(article_id, int): article_id = int(article_id)
        # Execute query on the table

        ## Get user id -> get_jwt_identity
        email = get_jwt_identity()

        cursor = get_cursor()
        try:
            query = """
            SELECT id 
            FROM auth
            WHERE email = %s;
            """
            cursor.execute(query, (email,))
            user_id = cursor.fetchone()[0]

            ## Get news id -> POST REQUEST
            news_id = article_id
            
            # Pus a query to database
            cursor.execute("START TRANSACTION")
            query = """
            INSERT INTO favourites (news_id, user_id)
            VALUES (%s, %s)
            """
            cursor.execute(query, (news_id, user_id))
            mysql.connection.commit()
            

        except Exception as e:
            mysql.connection.rollback()
            print(e)
            return_error("Internal Server Error!", 500)
        finally:
            cursor.close()
        
        return jsonify({"message": "Favourite news added successfully!"}), 201

    @server.route("/news/favourite", methods=["GET"])
    @jwt_required()
    def get_favourites():

        # Get user email
        email = get_jwt_identity()

        # Fetch user id
        cursor = get_cursor()
        try:
            cursor.execute("""SELECT id FROM auth WHERE email = %s""", (email,))
            user_id = cursor.fetchone()[0]

        except Exception as e:
            cursor.close()
            return_error("Internal Server Error"), 500

        # Fetch news id
        try:
            cursor.execute("""SELECT news_id FROM favourites WHERE user_id = %s""", (user_id,))
            data = cursor.fetchall()
            news_ids = [i[0] for i in data]            

        except Exception as e:
            cursor.close()
            return_error("Internal Server Error"), 500

        # Fetch news
        try:
            placeholders = ', '.join(['%s'] * len(news_ids))
            # id, title, source, date_published, popularity, content, author, category
            query = f"""
            SELECT n.title, n.source, n.date_published, n.popularity, n.content, a.name, c.name
            FROM news n
            INNER JOIN authors a ON n.author_id = a.id
            INNER JOIN categories c ON n.category_id = c.id            
            WHERE n.id IN ({placeholders})
            """
            cursor.execute(query, tuple(news_ids))
            data = cursor.fetchall()            
        except Exception as e:
            print(e)
        finally:
            cursor.close()
                
        res = []
        for idx, row in enumerate(data):
            news_instance = News(idx + 1, row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            res.append(news_instance.get_dict())
        return jsonify({"data": res}), 200            

    @server.route("/news", methods=["GET"])
    @jwt_required()
    @all_news_cache()
    def get_news():
        # Get the page, limit, sort by, order, category, author
        page = request.args.get("page", 1, type=int) # set default
        per_page = request.args.get("per_page", 5, type=int) # set default

        sort_on = request.args.get("sort_by", "date_published") # set default
        order = request.args.get("order", "desc") # set default

        category = request.args.get("category", None)
        author = request.args.get("author", None)
        
        offset = (page - 1) * per_page        

        ## Generate a key to identify if the key exists:
        key_list = [page, per_page, sort_on, order, category, author]
        key_list = [str(i) for i in key_list]
        key = '#'.join(key_list)        

        # Database Query
        cursor = get_cursor()
        try:
            query1 = """
            SELECT n.title, n.source, n.date_published, n.popularity, n.content, a.name, c.name
            FROM news n
            INNER JOIN authors a ON n.author_id = a.id
            INNER JOIN categories c ON n.category_id = c.id
            """                        

            query3 = """ORDER BY %(sort_on)s %(order)s LIMIT %(limit)s OFFSET %(offset)s;"""

            mapper = {
                "title": "n.title", "source": "n.source", "date_published": "n.date_published",
                "popularity": "n.popularity", "author": "a.name", "category": "c.name"
            }
            
            if sort_on: sort_on = mapper.get(sort_on, "n.date_published")
            
            conditions = []
            if category: conditions.append(f"c.name = %(category)s")
            if author: conditions.append(f"a.name = %(author)s")

            query2 = ""
            if conditions: query2 = "WHERE " + " AND ".join(conditions)

            query = ' '.join([query1, query2, query3])                                    

            input_params = {"limit": per_page, "offset": offset, "sort_on": sort_on, "order": order.upper(), "category": category, "author": author}
            cursor.execute(query, input_params)
            data = cursor.fetchall()
            
            # n.title, n.source, n.date_published, n.popularity, n.content, a.name, c.name
            articles = []
            for idx, row in enumerate(data):
                news_instance = News(idx + 1, row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                articles.append(news_instance.get_dict())                       

            res = {
                "page": page,
                "limit": per_page,
                "total_results": len(articles),
                "articles": articles
            }

        except Exception as e:
            print(e)
            return "Internal Server Error", 500
        finally:
            cursor.close()

        # Return Response        
        return res, 200

    @server.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        email, password = data.get("email", None), data.get("password", None)

        if not email or not password:
            return_error("Missing required credentials!", 400)

        def check_password(entered_password: str, hashed_password: str) -> bool:
            hashed_password = hashed_password.encode('utf-8')
            entered_password = entered_password.encode('utf-8')
            validate = bcrypt.checkpw(entered_password, hashed_password)
            return validate

        # Get Password for email and validate
        try:
            cursor = get_cursor()
            query = """SELECT password_hash FROM auth WHERE email = %s"""
            cursor.execute(query, (email, ))
            password_hash = cursor.fetchone()  # Always returns an array
            is_password_valid = False
            if password_hash:
                password_hash = password_hash[0]
                is_password_valid = check_password(password, password_hash)

            if not is_password_valid:
                return_error("Invalid credentials", 401)

        except Exception as e:
            print(e)
            return_error("Internal Server Error", 500)
        finally:
            cursor.close()

        # Create an access token
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(email, expires_delta=expires)

        # Return in response
        return jsonify({"message": "Login Successful", "access_token": access_token}), 200

    @server.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        email = data.get("email", None)
        password = data.get("password", None)

        if not email or not password:
            return_error("Missing Required Credentials", 400)

        # Hash password logic
        def hash_password(password: str) -> str:
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hash

        # Validate data from sql table
        password_hash = hash_password(password)
        cursor = get_cursor()
        try:
            query = """INSERT INTO auth (email, password_hash) VALUES (%s, %s)"""
            cursor.execute("START TRANSACTION")
            cursor.execute(query, (email, password_hash))
            mysql.connection.commit()

        except Exception as e:
            mysql.connection.rollback()
            print(e)
            return_error("Internal Server Error", 500)
        finally:
            cursor.close()

        # Return response if data is correct
        return jsonify({"message": "Registeration Successful!"}), 201

import functools, json
from app.database import redis_client
from flask import request, jsonify

def all_news_cache():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get from cache            
            page = request.args.get("page", 1, type=int) # set default
            per_page = request.args.get("per_page", 5, type=int) # set default
            
            query_params = request.args.to_dict()
            if page not in query_params: query_params["page"] = page
            if per_page not in query_params: query_params["per_page"] = per_page
            cache_key = f"news:{str(query_params)}"
            cached_response = redis_client.get(cache_key)
            if cached_response: 
                print("Returning cached data")
                return jsonify(json.loads(cached_response)), 200            

            # Run function
            response, statuscode = func(*args, **kwargs)

            # Cache data
            serialized_response = json.dumps(response, default=str)
            redis_client.set(cache_key, serialized_response, ex=600)

            return response, statuscode
        return wrapper
    return decorator
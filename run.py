from config import create_app
from app.routes import register_routes
from app.database import init_db

# Create Server
server = create_app()

# Initialize Database and redis
init_db(server)

# Register routes
register_routes(server)

PORT = 5001
if __name__ == "__main__":
    server.run(port=PORT, debug=True)
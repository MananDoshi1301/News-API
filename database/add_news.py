from mysql.connector import connect
import sys
from datetime import datetime

# Database connection
db_conn = connect(
    host="localhost",
    user="root",
    password="your_new_password",
    database="news_api"
)

if not db_conn:
    print("No db conn")
    sys.exit()

# Getting cursor
cursor = db_conn.cursor()

# articles
articles = [
  {
    "title": "Global Markets Rally Amid Economic Optimism",
    "content": "Stocks surged globally as investors bet on improving economic conditions.",
    "source": "Reuters",
    "category": "Finance",
    "author": "Jane Smith",
    "date_published": "2024-12-20T08:45:00Z",
    "popularity": 120
  },
  {
    "title": "New Discoveries in Quantum Computing",
    "content": "Scientists unveil breakthroughs in quantum algorithms with vast potential applications.",
    "source": "TechCrunch",
    "category": "Technology",
    "author": "John Doe",
    "date_published": "2024-12-22T14:30:00Z",
    "popularity": 95
  },
  {
    "title": "Climate Summit Yields Promising Agreements",
    "content": "World leaders agree to new policies aimed at reducing global emissions.",
    "source": "BBC",
    "category": "Environment",
    "author": "Alice Green",
    "date_published": "2024-12-19T10:00:00Z",
    "popularity": 140
  },
  {
    "title": "AI Revolutionizing Healthcare Diagnostics",
    "content": "Doctors are leveraging AI tools to detect diseases earlier than ever.",
    "source": "HealthLine",
    "category": "Health",
    "author": "Emma White",
    "date_published": "2024-12-18T09:15:00Z",
    "popularity": 180
  },
  {
    "title": "Sports Legend Announces Retirement",
    "content": "Fans around the world pay tribute to one of the greatest athletes in history.",
    "source": "ESPN",
    "category": "Sports",
    "author": "Tom Brown",
    "date_published": "2024-12-21T12:00:00Z",
    "popularity": 200
  },
  {
    "title": "Major Breakthrough in Renewable Energy",
    "content": "A new solar technology could make renewable energy more accessible worldwide.",
    "source": "The Verge",
    "category": "Environment",
    "author": "Lisa Blue",
    "date_published": "2024-12-23T11:30:00Z",
    "popularity": 110
  },
  {
    "title": "Advances in Space Exploration",
    "content": "NASA announces its next mission to explore the farthest reaches of the solar system.",
    "source": "NASA",
    "category": "Science",
    "author": "Sarah Gold",
    "date_published": "2024-12-24T16:00:00Z",
    "popularity": 170
  },
  {
    "title": "Economic Outlook for 2025: Key Insights",
    "content": "Economists share their predictions for global markets in the coming year.",
    "source": "Bloomberg",
    "category": "Finance",
    "author": "Michael Gray",
    "date_published": "2024-12-15T18:00:00Z",
    "popularity": 90
  },
  {
    "title": "Exploring Ancient Civilizations with AI",
    "content": "AI tools are providing archaeologists with new insights into ancient cultures.",
    "source": "National Geographic",
    "category": "History",
    "author": "Anna Black",
    "date_published": "2024-12-16T13:00:00Z",
    "popularity": 150
  },
  {
    "title": "Breakthroughs in Cancer Research",
    "content": "New therapies are showing promise in clinical trials for cancer treatment.",
    "source": "Scientific American",
    "category": "Health",
    "author": "David Brown",
    "date_published": "2024-12-17T08:00:00Z",
    "popularity": 130
  }
]

for article in articles:
    article["date_published"] = datetime.strptime(
        article["date_published"], "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%Y-%m-%d %H:%M:%S")


query = """
INSERT INTO news (title, content, source, date_published, popularity, author_id, category_id)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

# Pushing authors to database
try:
    db_conn.start_transaction()
    for article in articles:
        query = """INSERT IGNORE INTO authors (name) VALUES (%s);"""
        cursor.execute(query, (article["author"].lower(),))
    db_conn.commit()

except Exception as e:
    db_conn.rollback()
    print(e)

# Pushing categories to database
try:
    db_conn.start_transaction()
    for article in articles:
        query = """INSERT IGNORE INTO categories (name) VALUES (%s);"""
        cursor.execute(query, (article["category"].lower(),))
    db_conn.commit()
except Exception as e:
    db_conn.rollback()
    print(e)

# Pushing articles to database
try:
    db_conn.start_transaction()
    for article in articles:
        # Get author id
        cursor.execute("""SELECT id FROM authors WHERE name = %s""", (article["author"],))
        author_id = cursor.fetchone()[0]

        # Get category id
        cursor.execute("""SELECT id FROM categories WHERE name = %s""", (article["category"],))
        category_id = cursor.fetchone()[0]

        # Insert news
        cursor.execute(query, (article["title"], article["content"], article["source"], article["date_published"], article["popularity"], author_id, category_id))
    db_conn.commit()
except Exception as e:
    db_conn.rollback()
    print(e)


# Commit and close
db_conn.commit()
cursor.close()
db_conn.close()
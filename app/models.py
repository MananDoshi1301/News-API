# | id | title | source | date_published | popularity | author_id | category_id | content

# "Global Markets Rally Amid Economic Optimism",
# "Reuters",
# "Fri, 20 Dec 2024 08:45:00 GMT",
# 120,
# "Stocks surged globally as investors bet on improving economic conditions.",
# "jane smith",
# "finance"

class News:
    def __init__(self, id, title, source, date_published, popularity, content, author=None, category=None, author_id=None, category_id=None):
        self.id = id
        self.title = title
        self.source = source
        self.date_published = date_published
        self.popularity = popularity
        self.content = content
        self.author = author
        self.category = category
        self.author_id = author_id
        self.category_id = category_id
        
    def get_dict(self):
        d = {
            "id": self.id,
            "title": self.title.capitalize(),
            "source": self.source,
            "date_published": self.date_published,
            "popularity": self.popularity,
            "content": self.content,            
        }
        if self.author: d.update({"author": self.author.title()})
        if self.category: d.update({"category": self.category.capitalize()})

        return d
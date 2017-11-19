"""
    Главный файл для запуска приложения
"""


from flask import Flask
from routes import route


app = Flask(__name__)
app.config.from_pyfile("config.py")
route(app)
if __name__ == "__main__":
    app.run()

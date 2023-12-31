from flask import Flask
from markupsafe import escape
app = Flask(__name__)

@app.route('/') # '/' is http://localhost:5000/
@app.route('/user/<name>')
def user_page(name):
    return f'User: {escape(name)}'

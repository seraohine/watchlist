from flask import Flask , render_template
from markupsafe import escape
app = Flask(__name__)

name = 'Star Wang'
projects = [
    {'title': 'Algorithm'},
    {'title': 'Principles of computer composition'},
    {'title': 'C++ Learning'},
    {'title': 'Python Learning'},
    {'title': 'Flask Learning'},
    {'title': 'Tutorials To Making A OS'},
    {'title': 'OS Learning'},
    {'title': 'Django Learning'},
    {'title': 'Qt Learning'},
    {'title': 'Tutorials To Making A 2*2 Cube Solver By Python'},
]
@app.route('/') # '/' is http://localhost:5000/
def index():
    return render_template('index.html',name = name , projects = projects)


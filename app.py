from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.cli.command()
@click.option('--drop', is_flag = True ,  help = 'Create after drop.')
def initdb(drop):
    if drop:            #init the database
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')



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

class User(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(20))

class Projects(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    title = db.Column(db.String(60))



@app.route('/') # '/' is http://localhost:5000/
def index():
    user = User.query.first()
    project = Projects.query.all()
    return render_template('index.html',user = user , projects = projects)


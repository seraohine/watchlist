from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    content = db.Column(db.Text)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:  # init the database
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/')
def index():
    projects = Projects.query.all()
    return render_template('index.html', projects=projects)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Projects.query.get_or_404(project_id)

    if request.method == 'POST':
        project.content = request.form['content']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_project.html', project=project)


@app.route('/view/<int:project_id>')
def view_project(project_id):
    project = Projects.query.get_or_404(project_id)
    return render_template('view_project.html', project=project)


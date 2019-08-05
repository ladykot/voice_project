from flask import Flask, render_template
from webapp.model import db, Tasks


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/')
    def index():
        title = 'Список дел от Милены'
        tasks_milena = Tasks.query.with_entities(Tasks.task).all()
        return render_template("index.html", page_title=title, tasks_milena_list=tasks_milena)

    return app


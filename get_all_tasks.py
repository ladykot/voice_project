""" Чтобы записать данные в базу вне приложения, нужно подключиться к приложению
"""
from webapp import create_app
from webapp.main import main_dialogue


app = create_app()
with app.app_context():
    main_dialogue()


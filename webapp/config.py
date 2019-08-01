import os

basedir = os.path.abspath(os.path.dirname(__file__))  # абсолютный путь к директории директории вычисляется динамически
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "..", "webapp.db")

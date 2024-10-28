import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2

db = SQLAlchemy()

def createApp():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    app.secret_key = os.environ["SECRET_KEY"]
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    from .routes.auth import auth       
    app.register_blueprint(auth)
    from .routes.home import homeView       
    app.register_blueprint(homeView)
    from .routes.myProfile import myProfile       
    app.register_blueprint(myProfile)
    from .routes.mySubject import mySubject
    app.register_blueprint(mySubject)
    from .routes.task import task
    app.register_blueprint(task)
    
    with app.app_context():
        db.create_all() 
           
    return app

def getPostgresConnection():
    return psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        host=os.environ["DATABASE_HOST"],
        port="5432"
    )

def closePostgresConnection(connectionBd, cursorBd):
    cursorBd.close()
    connectionBd.close()
    
import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, flash, session
from utils.db import db

# Models


# Routes



def create_app():
    app = Flask(__name__)

    # TODO Configure .env uri
    #app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

    # TODO Change this to .env with another key.
    app.config['SECRET_KEY'] = "4e041161ab1f2548591d829ecdeb58bd3921a59462c714e2ccddbe02b69216d4"

    #db.init_app(app)


    @app.route('/')
    def index():
        return render_template("home.html")
    
    return app
import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, flash, session
from utils.db import db
from utils.hash import hash_pass
from sqlalchemy import select

# Models
from models.user import user_account

# Routes
from routes.admin import admin


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

    # TODO Change this to .env with another key.
    app.config['SECRET_KEY'] = "4e041161ab1f2548591d829ecdeb58bd3921a59462c714e2ccddbe02b69216d4"

    db.init_app(app)
    app.register_blueprint(admin, url_prefix="/admin")

    @app.route('/')
    def index():
        return redirect("/login")
    
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == 'POST':
            #quit session
            session.pop("user_name", None)
            session.pop("user_id", None)

            user = request.form['username']
            password = request.form['password']

            hashed_pass = hash_pass(password)

            query = select(user_account).where(user_account.c.user_name == user) \
                    .where(user_account.c.user_password == hashed_pass)

            result = db.session.execute(query).first()

            if result is None: 
                flash("Usuario y/o contrasena incorrectos", "error")
                return render_template("login.html")
            
            elif result.user_state != 0:
                flash("Usuario desactivado", "error")
                return render_template("login.html")

            else:
                session["user_name"] = result.user_name
                session["user_id"] = result.user_id
                return redirect("/admin")
        else:
            return render_template("login.html")
        
    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop("user_name", None)
        session.pop("user_id", None)
        return redirect("/")

    return app

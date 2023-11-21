import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, flash, session
from utils.db import db

# Models

# Routes
from routes.admin import admin


def create_app():
    app = Flask(__name__)

    # TODO Configure .env uri
    #app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

    # TODO Change this to .env with another key.
    app.config['SECRET_KEY'] = "4e041161ab1f2548591d829ecdeb58bd3921a59462c714e2ccddbe02b69216d4"

    #db.init_app(app)
    app.register_blueprint(admin, url_prefix="/admin")

    @app.route('/')
    def index():
        return render_template("login.html")
    
    @app.route('/login', methods=['POST', 'GET'])
    def login():
        
        return redirect("/admin")

    @app.route('/createUser/', methods=['GET', 'POST'])
    def create_user():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            if len(username) > 30 or not username.isalnum():
                flash('El nombre de usuario debe tener como máximo 30 caracteres alfanuméricos.', 'error')
                return redirect("/createUser/")
            if len(password) > 15 or not password.isalnum():
                flash('La contraseña debe tener como máximo 15 caracteres alfanuméricos.', 'error')
                return redirect("/createUser/")
            saveUser(username, password, email)
            flash('Usuario creado exitosamente', 'success')
            return redirect("/admin")
        return render_template('createUser.html')

    return app

def saveUser(username, password, email):
    filename = 'users.txt'
    with open(filename, 'a') as file:
        file.write(f'Username: {username}, Password: {password}, Email: {email}\n')
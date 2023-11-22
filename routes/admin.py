from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from utils.hash import hash_pass
from models.user import user_account
from sqlalchemy import insert
from utils.db import db

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.before_request
def before_request():
    if not "user_name" in session:
        return redirect(url_for("login"))

@admin.route('/')
def home():
    return render_template("home.html")


@admin.route('/create_user/', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if len(username) > 30 or not username.isalnum():
            flash('El nombre de usuario debe tener como máximo 30 caracteres alfanuméricos.', 'error')
            return render_template('createUser.html')
        if len(password) > 15 or not password.isalnum():
            flash('La contraseña debe tener como máximo 15 caracteres alfanuméricos.', 'error')
            return render_template('createUser.html')
        
        hashed_pass = hash_pass(password)
        
        query = insert(user_account).values(user_name=username, user_password=hashed_pass, user_email=email, user_state=0)
        print(query)
        db.session.execute(query)
        db.session.commit()

        flash('Usuario creado exitosamente', 'success')
        return render_template('createUser.html')
    
    elif request.method == 'GET':
        return render_template('createUser.html')
    

@admin.route('robots_drones', methods=["GET"])
def robots_drones():
    if request.method == 'GET':
        rows = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
        return render_template("robotsDrones.html", rows=rows)


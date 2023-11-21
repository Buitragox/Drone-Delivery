from flask import Blueprint, render_template, request, flash, redirect, url_for, session

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.route('/')
def home():
    return render_template("home.html")

@admin.route('/createUser/', methods=['GET', 'POST'])
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
        
        # TODO save to the database
        saveUser(username, password, email)

        flash('Usuario creado exitosamente', 'success')
        return render_template('createUser.html')
    
    elif request.method == 'GET':
        return render_template('createUser.html')

# TODO temp function
def saveUser(username, password, email):
    filename = 'users.txt'
    with open(filename, 'a') as f:
        f.write(f'Username: {username}, Password: {password}, Email: {email}\n')
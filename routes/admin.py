from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from utils.hash import hash_pass
from models.user import user_account
from sqlalchemy import insert
from utils.db import db

import requests

from flask import jsonify
admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")


@admin.before_request
def before_request():
    if not "user_name" in session:
        return redirect(url_for("login"))

     
def update_weather():
    weather_data = {
    'city': '',
    'temperature': '',
    'temperature_min': '',
    'temperature_max': '',
    'humidity': '',
    'speed': '',
    'description': ''
    }
    API_Wather = 'https://api.openweathermap.org/data/2.5/weather?q=Cali,co&APPID=bfc0a02f830fcebeea7ef589dacd1b1a'
    response = requests.get(API_Wather)
    if response.status_code == 200:
        data = response.json()
        weather_data['city'] = 'Cali'
        weather_data['temperature'] = data['main']['temp'] - 273.15
        weather_data['temperature_min'] = data['main']['temp_min'] - 273.15
        weather_data['temperature_max'] = data['main']['temp_max'] - 273.15
        weather_data['humidity'] = data['main']['humidity']
        weather_data['speed'] = round(data['wind']['speed'] * 18/5,2)
        weather_data['description'] = data['weather'][0]['description']
        return weather_data
    else:
        # Si la solicitud no fue exitosa, imprime el código de estado
        print(f'Error en la solicitud. Código de estado: {response.status_code}')
        return {}


@admin.route('/weather_data')
def weather_data():
    data = update_weather()
    return jsonify(data)


@admin.route('/')
def home():
    return render_template("home.html", weather_data = update_weather())


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


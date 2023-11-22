from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Flask
import requests

from flask import jsonify
admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

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


@admin.route('/createUser/', methods=['GET', 'POST'])
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
    elif request.method == 'GET':
        return render_template('createUser.html')
    

def saveUser(username, password, email):
    filename = 'users.txt'
    with open(filename, 'a') as file:
        file.write(f'Username: {username}, Password: {password}, Email: {email}\n')

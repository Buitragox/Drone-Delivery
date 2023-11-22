from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from utils.hash import hash_pass
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from utils.db import db
import requests
from os import getenv

from models.user import user_account
from models.robot_drone import robot_drone
from models.robot_state import robot_states
from models.maintenance import maintenance

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

google_api_key = getenv("GOOGLE_API_KEY")


@admin.before_request
def before_request():
    if request.endpoint != "admin.weather_data" and not "user_name" in session:
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
    api_url = "https://maps.googleapis.com/maps/api/js?key=" + google_api_key + "&callback=initMap"
    return render_template("home.html", weather_data=update_weather(), google_api_url=api_url)


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

    query = select(robot_drone, robot_states).where(robot_drone.c.robot_state == robot_states.c.robot_state)
    rows = db.session.execute(query).all()
    data = [[row.robot_id, ("Robot" if int(row.robot_type) == 0 else "Dron"), row.robot_reference, row.state_name] for row in rows]
        
    return render_template("robotsDrones.html", rows=data)



@admin.route('/registrar_mantenimiento/', methods=['GET', 'POST'])
def registrar_mantenimiento():
    if request.method == 'POST':
        robot_id = request.form['robot_id']
        maintenance_date = request.form['maintenance_date']
        technician_id = request.form['technician_id']
        description = request.form['description']
        
        query = insert(maintenance).values(robot_id=robot_id, 
                                           maintenance_date=maintenance_date, 
                                           technician_id=technician_id, 
                                           description=description)
        try:
            db.session.execute(query)
            db.session.commit()
            flash('Registro realizado con éxito', 'success')
        except IntegrityError:
            flash("Información invalida", "error")

        return render_template('registrarMantenimiento.html')
    
    elif request.method == 'GET':
        return render_template('registrarMantenimiento.html')
    

@admin.route('/registrar_robot/', methods=['GET', 'POST'])
def registrar_robot():
    if request.method == 'POST':
        robot_type = request.form['robot_type']
        robot_reference = request.form['robot_reference']
        
        query = insert(robot_drone).values(robot_type=robot_type, 
                                           robot_reference=robot_reference,
                                           robot_state=1)
        print(query)
        
        try:
            db.session.execute(query)
            db.session.commit()
            flash('Registro realizado con éxito', 'success')
        except IntegrityError as e:
            print(e)
            flash("Información invalida", "error")

        return render_template('registrarRobot.html')
    
    elif request.method == 'GET':
        return render_template('registrarRobot.html')
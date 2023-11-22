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

import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import re

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")
google_api_key = getenv("GOOGLE_API_KEY")

pedidos = [
    
]

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

@admin.route('/create_order/', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        iden = request.form['iden']
        print(type(iden), iden)
        if len(iden) < 10:
            flash('Coloque correctamente su identificación', 'error')
            return render_template('createOrder.html')
        name = request.form['name']
        email = request.form['email']
        nameadmin = request.form['nameadmin']
        dron = request.form['dron']
        service = request.form['opcion']
        if service == 'opcion1': service = 'Grabación de evento'
        else: service = 'Entrega'
        horaini = request.form['horaini']
        horafinal = request.form['horafini']
        descrip = request.form['descrip']
        patron_hora = re.compile(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$')
        if not (patron_hora.match(horaini) or patron_hora.match(horafinal)):
            flash('Debe ser una hora permitida (HH:MM:SS)', 'error')
            return render_template('createOrder.html')
        zona = request.form['zona']
        zonafini = request.form['zonafini']
        pedidos.append( {'id': len(pedidos), 'identificacion': iden, 'nombre': name, 'email': email, 'nameadmin': nameadmin, 
                         'dron': dron, 'service': service, 'horainicio': horaini, 'horafinal': horafinal, 'descripcion': descrip,
                         'zona': zona, 'zonafinal': zonafini} )
        return render_template('createOrder.html')
    elif request.method == 'GET':
        return render_template('createOrder.html')
    
@admin.route('/aceptar/<int:pedido_id>')
def aceptar_pedido(pedido_id):
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        send_qr(pedido['email'])
        pedidos.remove(pedido)
        return render_template('orders.html', pedidos = pedidos)
    else:
        return "Pedido no encontrado."
    
@admin.route('/rechazar/<int:pedido_id>')
def rechazar_pedido(pedido_id):
    pedido = next((p for p in pedidos if p['id'] == pedido_id), None)
    if pedido:
        pedidos.remove(pedido)
        return render_template('orders.html', pedidos = pedidos)
    else:
        return "Pedido no encontrado."
    
def send_qr(email):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(email)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qr.png")

    subject = 'Código QR para tu pedido'
    body = 'Adjunto encontrarás el código QR para tu pedido.'
    sender_email = 'uwudelivery150@gmail.com'
    sender_password = getenv("PASSWORD")

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))
    attachment = open("qr.png", "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= qr.png")

    message.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPException as e:
        print(f"Error al iniciar sesión: {e}")
    text = message.as_string()
    server.sendmail(sender_email, email, text)
    server.quit()
    
@admin.route( '/orders/', methods=[ 'GET', 'POST'] )
def orders():
    return render_template('orders.html', pedidos = pedidos)


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
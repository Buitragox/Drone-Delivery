from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from utils.hash import hash_pass
from models.user import user_account
from sqlalchemy import insert
from utils.db import db
import requests
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

pedidos = [
    {"id": 1, "nombre": "Dilan Correa", "carrera": "Ingenieria Sistemas", "descripcion": "Rodilla", "email": "dilancito2546@gmail.com", "telefono": "123456789"},
    {"id": 2, "nombre": "Jhoan Buitrago", "carrera": "Ingenieria Sistemas", "descripcion": "Chocolate", "email": "jhoanuitrago@gmail.com", "telefono": "987654321"}
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
    load_dotenv()
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
    sender_password = os.getenv("PASSWORD")

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
    server.login(sender_email, sender_password)
    text = message.as_string()
    server.sendmail(sender_email, email, text)
    server.quit()
    
@admin.route( '/orders/', methods=[ 'GET', 'POST'] )
def orders():
    return render_template('orders.html', pedidos = pedidos)


@admin.route('robots_drones', methods=["GET"])
def robots_drones():
    if request.method == 'GET':
        rows = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
        return render_template("robotsDrones.html", rows=rows)


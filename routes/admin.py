from flask import Blueprint, render_template, request, flash, redirect, url_for, session

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.route('/')
def home():
    return render_template("home.html")
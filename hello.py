from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>hello world</p>"


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/listCustomer")
def listCustomer():
    return render_template('customer_management.html')

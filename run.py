from flask import Flask


app = Flask(__name__)


@app.route("/characters")
def characters():
    return "<p>Hello, World!</p>"


@app.route("/location")  # name=earth&type=planet
def location():
    return "<p>Hello, World!</p>"

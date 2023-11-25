from flask import Flask, render_template
from flask_ngrok import run_with_ngrok
from routes.location import location
from routes.predict import prediction
from routes.sub import subcrop
from routes.crop import response_data
from routes.marketdata import marketdata
from routes.train import train


app = Flask(__name__)

app.register_blueprint(location)
app.register_blueprint(prediction)
app.register_blueprint(subcrop)
app.register_blueprint(marketdata)
app.register_blueprint(train)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("hello.html")


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("aboutus.html")

@app.route('/loc3')
def loc3():
    return render_template('loc3.html')
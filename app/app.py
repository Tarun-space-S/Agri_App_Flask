from flask import Flask, render_template
from flask_ngrok import run_with_ngrok
from routes.location import location
from routes.predict import prediction
from routes.sub import subcrop
from routes.crop import response_data



app = Flask(__name__)

app.register_blueprint(location)
app.register_blueprint(prediction)
app.register_blueprint(subcrop)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("hello.html")

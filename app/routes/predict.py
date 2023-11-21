from flask import Blueprint, render_template, request
from routes.crop import response_data
import numpy as np
import pickle



final_model = pickle.load(open('models/model_to_put_to_app.pkl','rb'))
ss  = pickle.load(open('models/standscaler.pkl','rb'))
ms = pickle.load(open('models/minmaxscaler.pkl','rb'))


prediction = Blueprint('prediction', __name__)

@prediction.route('/weather', methods=['POST', 'GET'])
def get_weather():
    return render_template("weather.html",response_data=response_data)

@prediction.route('/model', methods=['GET'])
def model():
    return render_template("index.html",response_data=response_data)


@prediction.route("/predict",methods=['POST','GET'])
def predict():
    N = float(request.form['Nitrogen'])
    P = float(request.form['Phosphorus'])
    K = float(request.form['Potassium'])
    ph = float(request.form['Ph'])
    response_data.update({'N':N,'P':P,'K':K,'ph':ph})
    temp=float(response_data['average_temperature'])
    humidity=float(response_data['average_humidity'])
    rainfall=float(response_data['monthly_rainfall'])


    if N<0 or N > 10000 or P<0 or P>5000 or K>10000 or K<0 or ph<1 or ph>14 or temp < -90 or temp>55 or humidity<0 or humidity>100 or rainfall<0 or  rainfall>11000:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
        
    

    features = np.array([[N,P,K,temp,humidity,ph,rainfall]])
    transformed_features = ms.transform(features)
    transformed_features = ss.transform(transformed_features)
    prediction = final_model.predict(transformed_features)

    # feature_list = [N, P, K, temp, humidity, ph, rainfall]
    # single_pred = np.array(feature_list).reshape(1, -1)

    # scaled_features = ms.transform(single_pred)
    # final_features = sc.transform(scaled_features)
    # prediction = model.predict(final_features)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
    else:   
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
    response_data.update({'main_crop':crop,'result':result})

    
    return render_template('index.html',response_data=response_data)

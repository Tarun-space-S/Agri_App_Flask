from flask import Blueprint, render_template, request,jsonify
from routes.crop import response_data
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)


message='Please Click the Train Button'
complete=0
acc={'layer1':0,'layer2':0,'layer3':0}  

train = Blueprint('train', __name__)



@train.route('/display', methods=['POST', 'GET'])
def display():
    global message
    global complete
    global acc
    return render_template("sample.html")

@train.route('/train_status', methods=['POST', 'GET'])
def get_status():
    global message
    global complete
    global acc
    return jsonify(status=message,complete=complete,acc=acc)

@train.route('/train', methods=['POST', 'GET'])
def train_model():
    global message
    global complete
    global acc
    acc={'layer1':0,'layer2':0,'layer3':0}
    complete=0
    message='Please wait while we are training the model for you'
    dir = response_data['dataset_loc'] 
    # dir=r'dataset\KL_138_30-Nov-2022_30-Oct-2023.csv'
    df = pd.read_csv(dir)

    message='Dataset Loaded'
    #convert 'Price date' column into datetime datatype
    df.rename(columns={'Price Date': 'Price_Date'}, inplace=True)
    df['Price_Date'] = pd.to_datetime(df['Price_Date'])

    # Extract day, month, year, quater, and day name from 'Price_Date' column
    df['Price_Date_month'] = df['Price_Date'].dt.month
    df['Price_Date_day'] = df['Price_Date'].dt.day
    df['Price_Date_year'] = df['Price_Date'].dt.year
    df['Price_Date_quarter'] = df['Price_Date'].dt.quarter
    df['Price_Date_day_week'] = df['Price_Date'].dt.day_name()

    # now we can safely drop 'Price Date' column
    df.drop('Sl no.', axis=1, inplace=True) # drop 'Sl no.' column

    df.drop(['Price_Date'], axis=1, inplace=True)
    df.drop(['Price_Date_year'], axis=1, inplace=True)
    ori=df.copy()


    message='Dataset Preprocessed'

    df.head()

    en_att = ['District Name','Market Name','Commodity','Variety','Grade','Price_Date_day_week','Price_Date_quarter','Price_Date_month','Price_Date_day']

    for i in en_att:
        le = LabelEncoder()
        df[i] = le.fit_transform(df[i])
        # now you can save it to a file
        with open('models/price/le_'+i+'.pkl', 'wb') as f:
            pickle.dump(le, f)
    df=pd.get_dummies(df, columns=en_att)
    en=df.copy()

    # Create a mapping between the original values and their one-hot encoded columns
    one_hot_mapping = {col: col.split('_')[-1] for col in en.columns}
    with open('models/price/one_hot_mapping.pkl', 'wb') as mapping_file:
        pickle.dump(one_hot_mapping, mapping_file)
    # one hot encoding

    message='Dataset Encoded'

    move=['Modal Price (Rs./Quintal)','Min Price (Rs./Quintal)','Max Price (Rs./Quintal)']
    new_order = [col for col in df.columns if col not in move] + move
    df = df[new_order]

    train = df.select_dtypes(exclude='object')

    x=train
    y=train[['Modal Price (Rs./Quintal)','Min Price (Rs./Quintal)','Max Price (Rs./Quintal)']]

    # 20% data as validation set
    X_train,X_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=22)

    message='Dataset Splitted'

    ############################################## Min Price ########################################################
    X_train_min = X_train.drop(columns=['Modal Price (Rs./Quintal)','Max Price (Rs./Quintal)','Min Price (Rs./Quintal)'], axis=1,)
    X_test_min=X_test.drop(columns=['Modal Price (Rs./Quintal)','Max Price (Rs./Quintal)','Min Price (Rs./Quintal)'], axis=1,)
    y_test_min=y_test['Min Price (Rs./Quintal)']
    y_train_min=y_train['Min Price (Rs./Quintal)']
    RF = RandomForestRegressor().fit(X_train_min,y_train_min)
    # print('Train set accuracy: %f'%RF.score(X_train_min,y_train_min))
    # print('Test set accuracy: %f'%RF.score(X_test_min,y_test_min))
    with open('models/price/min_price.pkl', 'wb') as file:
        pickle.dump(RF, file)
    y1_min=RF.predict(X_test_min)

    message='First Model Trained'
    acc['layer1']=RF.score(X_test_min,y_test_min)*100
    ############################################## Max Price ########################################################
    X_train_max = X_train.drop(columns=['Modal Price (Rs./Quintal)','Max Price (Rs./Quintal)'], axis=1,)
    X_test_max=X_test.drop(columns=['Modal Price (Rs./Quintal)','Max Price (Rs./Quintal)'], axis=1,)
    X_test_max['Min Price (Rs./Quintal)']=y1_min
    y_test_max=y_test['Max Price (Rs./Quintal)']
    y_train_max=y_train['Max Price (Rs./Quintal)']

    RF1 = RandomForestRegressor().fit(X_train_max,y_train_max)
    # print('Train set accuracy: %f'%RF1.score(X_train_max,y_train_max))
    # print('Test set accuracy: %f'%RF1.score(X_test_max,y_test_max))
    with open('models/price/max_price.pkl', 'wb') as file:
        pickle.dump(RF1, file)
    y1_max=RF1.predict(X_test_max)
    message='Second Model Trained'
    acc['layer2']=RF1.score(X_test_max,y_test_max)*100
    ############################################## Modal Price ########################################################
    X_train_mod = X_train.drop(columns=['Modal Price (Rs./Quintal)'], axis=1,)
    X_test_mod=X_test.drop(columns=['Modal Price (Rs./Quintal)'], axis=1,)
    X_test_mod['Max Price (Rs./Quintal)']=y1_max
    y_test_mod=y_test['Modal Price (Rs./Quintal)']
    y_train_mod=y_train['Modal Price (Rs./Quintal)']

    RF2 = RandomForestRegressor().fit(X_train_mod,y_train_mod)
    # print('Train set accuracy: %f'%RF2.score(X_train_mod,y_train_mod))
    # print('Test set accuracy: %f'%RF2.score(X_test_mod,y_test_mod))
    with open('models/price/mod_price.pkl', 'wb') as file:
        pickle.dump(RF2, file)
    y1_mod=RF2.predict(X_test_mod)
    message='Third Model Trained'
    acc['layer3']=RF2.score(X_test_mod,y_test_mod)*100
    message='Final Accuracy: '+str(acc['layer3'])+'%'
    complete=1
    
    return jsonify(message="SUCCESSFUL",complete=complete)

@train.route('/predict_price', methods=['POST', 'GET'])
def predict_price():
    global message
    global complete
    global acc

    # get values from the from 
    district = request.form['district']
    market = request.form['market']
    commodity = request.form['commodity']
    variety = request.form['variety']
    grade = request.form['grade']


    complete=0
    message='Please wait while we are predicting the price for you'

    

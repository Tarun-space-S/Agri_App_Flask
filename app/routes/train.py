from flask import Blueprint, render_template, request,jsonify
from routes.crop import response_data
import pandas as pd
import io
import base64
from datetime import datetime
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)


message='Please Click the Train Button'
complete=0
acc={'layer1':0,'layer2':0,'layer3':0}  
data=None
en_att=None
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
    global en_att
    global data
    acc={'layer1':0,'layer2':0,'layer3':0}
    complete=0
    message='Please wait while we are training the model for you'
    # dir = response_data['dataset_loc'] 
    dir=r'dataset\KK_19_08-Dec-2022_08-Nov-2023.csv'
    df = pd.read_csv(dir)
    data=df.copy()
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

@train.route('/price_input', methods=['POST', 'GET'])
def price_input():
    global message
    global complete
    global acc
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    district_list = data['District Name'].unique().tolist()
    district_list.sort()
    market_list = data['Market Name'].unique().tolist()
    market_list.sort()
    commodity_list = data['Commodity'].unique().tolist()
    commodity_list.sort()
    variety_list = data['Variety'].unique().tolist()
    variety_list.sort()
    grade_list = data['Grade'].unique().tolist()
    grade_list.sort()

    

    return render_template("price.html",district_list=district_list,market_list=market_list,commodity_list=commodity_list,variety_list=variety_list,grade_list=grade_list,today_date=today_date)


def pred_price(district,market,commodity,variety,grade,date):
    global en_att
    input_data=[[district,market,commodity,variety,grade,date]]
    input_data=pd.DataFrame(input_data,columns=['District Name','Market Name','Commodity','Variety','Grade','Price Date'])

    input_data['Price_Date'] = pd.to_datetime(input_data['Price Date']) 
    input_data['Price_Date_month'] = input_data['Price_Date'].dt.month
    input_data['Price_Date_day'] = input_data['Price_Date'].dt.day 
    input_data['Price_Date_year'] = input_data['Price_Date'].dt.year
    input_data['Price_Date_quarter'] = input_data['Price_Date'].dt.quarter
    input_data['Price_Date_day_week'] = input_data['Price_Date'].dt.day_name()
    # now we can safely drop 'Price Date' column
    input_data.drop(['Price_Date','Price Date','Price_Date_year'], axis=1, inplace=True)
    # now we move on to encoding
    for i in en_att:
        with open('models/price/le_'+i+'.pkl', 'rb') as f:
            leo = pickle.load(f) 
        input_data[i] = leo.transform(input_data[i])

    fine=input_data.loc[0]
    fine=fine.to_dict()
    for i in en_att:
        fine[i]=f"{i}_{fine[i]}"
    feed={}
    with open('models/price/one_hot_mapping.pkl', 'rb') as file:
            one_hot_mapping = pickle.load(file)
    for column, encoded_column in one_hot_mapping.items():
        # print(column, encoded_column)
        if column in ['Min Price (Rs./Quintal)','Max Price (Rs./Quintal)','Modal Price (Rs./Quintal)']:
            feed[column]=0
        elif column in fine.values():
            feed[column]=True
        else:
            feed[column]=False
    lesgo=pd.DataFrame(feed,index=[0])
    lesgo.drop(['Min Price (Rs./Quintal)','Max Price (Rs./Quintal)','Modal Price (Rs./Quintal)'], axis=1, inplace=True)

    with open('models/price/min_price.pkl', 'rb') as f:
        min_price = pickle.load(f)
    with open('models/price/max_price.pkl', 'rb') as f:
        max_price = pickle.load(f)
    with open('models/price/mod_price.pkl', 'rb') as f:
        mod_price = pickle.load(f)
    
    min_price=min_price.predict(lesgo)
    lesgo['Min Price (Rs./Quintal)']=min_price
    max_price=max_price.predict(lesgo)
    lesgo['Max Price (Rs./Quintal)']=max_price
    mod_price=mod_price.predict(lesgo)
    return min_price,max_price,mod_price

def trend_graph(district,market,commodity,variety,grade):
    dates = pd.date_range('2023-01-01', periods=30)
    min_prices = []
    max_prices = []
    modal_prices = []
    for date in dates:
        min_price,max_price,mod_price=pred_price(district,market,commodity,variety,grade,date)
        min_prices.append(min_price)
        max_prices.append(max_price)
        modal_prices.append(mod_price)
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, min_prices, label='Min Price')
    plt.plot(dates, max_prices, label='Max Price')
    plt.plot(dates, modal_prices, label='Modal Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Monthly Price Trend for ' + commodity + ' in ' + market + ' market')
    plt.legend()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph = base64.b64encode(img.getvalue()).decode()   

    return graph


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
    date = request.form['date']
    min_price,max_price,mod_price=pred_price(district,market,commodity,variety,grade,date)
    response_data.update({'min_price':min_price,'max_price':max_price,'mod_price':mod_price,'price_date':date})
    graph=trend_graph(district,market,commodity,variety,grade)
    response_data.update({'graph':graph})

    return render_template("end.html",response_data=response_data)

    

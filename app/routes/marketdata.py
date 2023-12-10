from flask import Blueprint, render_template, request,jsonify
from routes.crop import response_data
import os
import time
import pandas as pd
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select


dataset_message='Please Click the Get Data Button'
select='none'
years=1
complete=0
marketdata = Blueprint('marketdata', __name__)


@marketdata.route('/get_status', methods=['POST', 'GET'])
def get_status():
    return jsonify(status=dataset_message,complete=complete)


@marketdata.route('/market', methods=['POST', 'GET'])
def market():
    global select
    global dataset_message
    global years
    return render_template("dataset.html",response_data=response_data,dataset_message=dataset_message)

@marketdata.route('/input', methods=['POST', 'GET'])
def inpp():
    global select
    global dataset_message
    global years

    proceed=1
    select=request.form['in_state']
    years=request.form['in_years']
    print(select,years)
    return render_template("dataset.html",response_data=response_data,dataset_message=dataset_message,proceed=proceed)

@marketdata.route('/marketdata',methods=['POST','GET'])
def market_data():

    global complete
    global dataset_message
    global select
    global years
    

    complete=0
    dataset_message='Please wait while we are fetching the dataset for you'
    maincrop=response_data['main_crop']
    df=pd.read_csv("dataset/sys/output.csv")
    result=df[df['name']==maincrop]
    result=result.to_dict('records')
    value=result[0]['value']
    commodity=value#banana
    if select!='none':
        state=str(select)
    else:
        state=response_data['state_code']
    
    years=int(years)
    

    state_data = pd.read_csv('dataset/sys/state.csv')
    matched_state = state_data[state_data['code'] == state]
    if not matched_state.empty:
        state_name= matched_state.iloc[0]['state']



    commodity_data = pd.read_csv('dataset/sys/commodity.csv')
    matched_commodity = commodity_data[commodity_data['code'] == commodity]
    if not matched_commodity.empty:
        commodity_name= matched_commodity.iloc[0]['commodity']
        
        

    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    target_directory=current_directory+"\dataset"
    print("Current Directory:", current_directory)
    print("Target Directory:", target_directory)
    driver_path=current_directory+"\models\msedgedriver.exe"

    today = date.today()
    dateFrom = today.replace(year=today.year-int(years)).strftime("%d-%b-%Y")
    dateTo = today.replace(month=today.month-1).strftime("%d-%b-%Y")
    frame = "from date :"+dateFrom,"to date:"+dateTo
    print(commodity,state,dateFrom,dateTo,commodity_name,state_name)


    options = Options()
    options.use_chromium = True
    options.add_experimental_option('prefs', {
        'download': {
            'default_directory': target_directory,
        }
    })

    driver = webdriver.Edge(options=options)
    dataset_message = 'driver initiated successfully'
    url ="https://agmarknet.gov.in/Default.aspx"

    url1=f"https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity={commodity}&Tx_State={state}&Tx_District=0&Tx_Market=0&DateFrom={dateFrom}&DateTo={dateTo}&Fr_Date={dateFrom}&To_Date={dateTo}&Tx_Trend=0&Tx_CommodityHead={commodity_name}&Tx_StateHead={state_name}&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"
    driver.get(url1)


    data_name_format=state+"_"+str(commodity)+"_"+dateFrom+" "+dateTo+".csv"
    
    dataset_message = 'Submitting values'
    time.sleep(5)


    export_button = driver.find_element(By.ID, "cphBody_ButtonExcel")
    export_button.click()
    dataset_message = 'Dataset Aquired set to Download'
    time.sleep(10)

    driver.close()
    dataset_message = 'Driver Teminated'
    xls_file = target_directory + "\Agmarknet_Price_Report.xls"
    raw = pd.read_html(xls_file)
    final = raw[0]
    final = final.to_csv(target_directory + f"\{data_name_format}", index=False)
    dataset_message = 'data saved successfully to csv file'

    file_path = xls_file

    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    else:
        print(f"File '{file_path}' does not exist.")

    dataset_message = "Dataset retrived successfully for " + state + " " + str(commodity) + " " + dateFrom + " " + dateTo + " as csv with name" + data_name_format
    response_data.update({'dataset_loc':target_directory + f"\{data_name_format}"})
    complete = 1
        # return render_template("dataset.html",dataset_message=dataset_message,response_data=response_data)
    return jsonify(message="SUCCESSFUL",response_data=response_data)





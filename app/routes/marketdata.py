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
complete=0
marketdata = Blueprint('marketdata', __name__)


@marketdata.route('/get_status', methods=['POST', 'GET'])
def get_status():
    return jsonify(status=dataset_message,complete=complete)


@marketdata.route('/market', methods=['POST', 'GET'])
def market():
    global select
    global dataset_message
    if request.method == 'POST':
        select=request.form['state']
    

    return render_template("dataset.html",response_data=response_data,dataset_message=dataset_message)


@marketdata.route('/marketdata',methods=['POST','GET'])
def market_data():

    global complete
    global select
    global dataset_message
    complete=0
    dataset_message='Please wait while we are fetching the dataset for you'
    
    
    maincrop=response_data['main_crop']
    df=pd.read_csv("dataset/sys/output.csv")
    result=df[df['name']==maincrop]
    result=result.to_dict('records')
    value=result[0]['value']
    print(value)



    commodity_value=value#banana
    if select!='none':
        state=str(select)
    else:
        state=response_data['state_code']
    



    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    target_directory=current_directory+"\dataset"
    print("Current Directory:", current_directory)
    print("Target Directory:", target_directory)
    driver_path=current_directory+"\models\msedgedriver.exe"
    url ="https://agmarknet.gov.in/Default.aspx"

    today = date.today()
    d1 = today.replace(year=today.year-1).strftime("%d-%b-%Y")
    d2 = today.replace(month=today.month-1).strftime("%d-%b-%Y")
    frame = "from date :"+d1,"to date:"+d2
    print(state,frame)


    options = Options()
    options.use_chromium = True
    options.add_experimental_option('prefs', {
        'download': {
            'default_directory': target_directory,
        }
    })

    driver = webdriver.Edge(options=options)
    dataset_message = 'driver initiated successfully'

    driver.get(url)
    driver.minimize_window()
    dataset_message = 'opened agmarknet.gov.in successfully'

    data_name_format = state + "_" + str(commodity_value) + "_" + d1 + "_" + d2 + ".csv"

    close = driver.find_element(By.CSS_SELECTOR, "a.close")
    close.click()
    dataset_message ='Pushing Values'
    price_dropdown = Select(driver.find_element(By.NAME, "ddlArrivalPrice"))
    price_dropdown.select_by_value("0")

    commodity_dropdown = Select(driver.find_element(By.ID, "ddlCommodity"))
    commodity_dropdown.select_by_value(str(commodity_value))

    state_dropdown = Select(driver.find_element(By.ID, "ddlState"))
    state_dropdown.select_by_value(state)

    district_dropdown = Select(driver.find_element(By.ID, "ddlDistrict"))
    district_dropdown.select_by_value("0")

    market_dropdown = Select(driver.find_element(By.ID, "ddlMarket"))
    market_dropdown.select_by_value("0")

    date_field = driver.find_element(By.ID, "txtDate")
    date_field.clear()
    date_field.send_keys(d1)

    

    go_button = driver.find_element(By.ID, "btnGo")
    go_button.click()

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

    complete = 1
    dataset_message = "Dataset retrived successfully for " + state + " " + str(commodity_value) + " " + d1 + " " + d2 + " as csv with name" + data_name_format
        # return render_template("dataset.html",dataset_message=dataset_message,response_data=response_data)
    return jsonify(message="SUCCESSFUL",response_data=response_data)





from flask import Blueprint, render_template, request,jsonify
from routes.crop import response_data
import os
import time
import pandas as pd
from datetime import date
from selenium.webdriver.support.ui import Select
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
# from routes.crop import response_data
# from routes.crop import response_data

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
    no_of_years=1



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


    options = EdgeOptions()
    options.use_chromium = True
    options.add_experimental_option("prefs", {"download.default_directory": target_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True})

    # driver_path=r"C:\Users\tarbo\Downloads\msedgedriver.exe"

    driver = Edge(executable_path=driver_path,options=options)
    dataset_message='driver initiated successfully'
    driver.minimize_window()

    # get required data for searching in web
    driver.get(url)
    dataset_message='opened agmarknet.gov.in successfully'

    data_name_format=state+"_"+str(commodity_value)+"_"+d1+"_"+d2+".csv"
    # time.sleep(2)
    close = driver.find_element_by_css_selector("a.close")
    close.click()
    # time.sleep(5)
    # Price/Arrivals we select price
    pa=Select(driver.find_element_by_name("ddlArrivalPrice"))
    pa.select_by_value ("0")

    pa=Select(driver.find_element_by_id("ddlCommodity"))
    pa.select_by_value (str(commodity_value))

    pa=Select(driver.find_element_by_id("ddlState"))
    pa.select_by_value (state)

    #select district
    pa=Select(driver.find_element_by_id("ddlDistrict"))
    pa.select_by_value("0")

    #select market
    pa=Select(driver.find_element_by_id("ddlMarket"))
    pa.select_by_value("0")

    # pa=driver.find_element_by_id("txtDateTo")
    # pa.clear()
    # pa.send_keys(d2)

    pa=driver.find_element_by_id("txtDate")
    pa.clear()
    pa.send_keys(d1)

    dataset_message='values entered successfully'

    #click on go button
    button = driver.find_element_by_id("btnGo")
    button.click()
    
    # wait for 10 sec
    time.sleep(5)

    #click on export to excel
    pa=driver.find_element_by_id("cphBody_ButtonExcel")
    pa.click()
    dataset_message='accessed data successfully'
    # wait for 10 sec
    time.sleep(10)
    
    dataset_message='data downloaded successfully'
    #close the browser
    driver.minimize_window()
    

    xls_file=target_directory+"\Agmarknet_Price_Report.xls"
    raw=pd.read_html(xls_file)
    final=raw[0]
    final=final.to_csv(target_directory+f"\{data_name_format}",index=False)
    dataset_message='data saved successfully to csv file'
    file_path = xls_file
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    else:
        print(f"File '{file_path}' does not exist.")
    response_data.update({'dataset_status':dataset_message,'dataset_loc':target_directory+f"\{data_name_format}"})
    complete=1
    dataset_message="Dataset retrived successfully for "+state+" "+str(commodity_value)+" "+d1+" "+d2+" as csv with name"+data_name_format
    
    # return render_template("dataset.html",dataset_message=dataset_message,response_data=response_data)
    return jsonify(message="SUCCESSFUL",response_data=response_data)





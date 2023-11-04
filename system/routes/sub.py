from flask import Blueprint, render_template
from routes.crop import response_data
import pandas as pd
import math


subcrop=Blueprint('subcrop',__name__)

@subcrop.route('/subcrops', methods=['GET'])
def subcrops():
    def min_dis(pivot,data):
        result={}
        for i in data:
            result[i]=0
            print(result)
            for j in range(len(data[i])):
                result[i]+=math.pow((pivot[j]-data[i][j]),2)
            result[i]=math.sqrt(result[i])
        result=sorted(result.items(),key=lambda x:x[1])
        return result
    
    usr_input=response_data['main_crop']

    sd=pd.read_csv('dataset/subdata.csv')
    md=pd.read_csv('dataset/maindata.csv')
    sd=pd.DataFrame(sd)
    md=pd.DataFrame(md)
    md.set_index('Crop',inplace=True)
    sd.set_index('label',inplace=True)
    # print(sd)

    sub=md.loc[usr_input]
    sub=sub.tolist()
    # print(sub)

    final={}
    for i in sub:
        dat=sd.loc[i]
        dat=dat.tolist()
        final[i]=dat
    # print(final) 
    pivot=[response_data['N'],response_data['P'],response_data['K'],response_data['average_temperature'],response_data['average_humidity'],response_data['ph'],response_data['monthly_rainfall']]
    sub_crops=min_dis(pivot,final)
    response_data.update({'sub_crops':sub_crops})
    return render_template("index.html",response_data=response_data)
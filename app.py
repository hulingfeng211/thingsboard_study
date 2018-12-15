# -*- coding:utf-8 -*- 

from tornado.options import parse_command_line,define,options
from tornado.log import gen_log
from tornado.gen import IOLoop,coroutine,sleep
from tornado.httpclient import AsyncHTTPClient
import requests 
import json 
import random 
import time 
import sys

#curl -X POST --header 'Content-Type: application/json' 
# --header 'Accept: application/json' 
# -d '{"username":"tenant@thingsboard.org", "password":"tenant"}'
#  'http://THINGSBOARD_URL/api/auth/login'

define('token',default=None,type=str,help='device token')

url_prefix="http://www.you00.cn/api"
headers={'content-type':'application/json'}
username='user@163.com'
password='password'

attributes = ['wind_speed','wind_direction','rainfall','light','UVI','temperature','humidity','pressure']

def get_access_token(username,password):
    """
    :return {"token":'xxx',"refreshToken":"xxx"}
    """
    
    url=url_prefix+"/auth/login"
    data=json.dumps({'username':username,'password':password})
    
    res=requests.post(url,data=data,headers=headers)
    #print(res.text)
    assert res.status_code==200 
    return res.json()

# attributes-data 
# {"firmware_version":"1.0.1", "serial_number":"SN-001"}
#curl -v -X POST -d @attributes-data.json
#  http://$THINGSBOARD_HOST:$THINGSBOARD_PORT/api/
# v1/$ACCESS_TOKEN/attributes --header "Content-Type:application/json"

@coroutine
def upload_attribute_data():
    """
    data format like flow.
    {"attribute1":"value1",
     "attribute2":true, "attribute3":42.0, "attribute4":73}
    """
    gen_log.info("upload_attribute_data")
    try:
        data={"firmware_version":"1.0.1", "serial_number":"SN-001"}
        url=url_prefix+'/v1/{}/attributes'.format(token)
        res=yield AsyncHTTPClient().fetch(url,method='POST',body=json.dumps(data),headers=headers)
        #res=requests.post(url,data=json.dumps(data),headers=headers)
        gen_log.info(res.body)
    except Exception as ex:
        gen_log.error(ex)
    
    IOLoop.current().add_timeout(time.time()+1,upload_attribute_data)
#=============

# telemetry-data.json 
# {"temperature":21, "humidity":55.0, "active": false}
# curl -v -X POST -d @telemetry-data.json
#  http://$THINGSBOARD_HOST:$THINGSBOARD_PORT/api/
# v1/$ACCESS_TOKEN/telemetry --header "Content-Type:application/json"

@coroutine
def upload_telemetry_data():
    """
    In case your device is able to get the client-side timestamp, you can use following format
    {"ts":1451649600512, "values":{"key1":"value1", "key2":"value2"}}
    """
    gen_log.info("upload_telemetry_data")
    try:
        data=[{attr:random.randint(20,100)} for attr in attributes if attr!='temperature']
        # data={"temperature":random.randint(20,100), 
        # "humidity":random.randint(20,100),
        # "other":random.randint(-60,60),
        #  "active": False}
        url=url_prefix+'/v1/{}/telemetry'.format(token)
        res=yield AsyncHTTPClient().fetch(url,method='POST',body=json.dumps(data),headers=headers)
        #res=requests.post(url,data=json.dumps(data),headers=headers)
        gen_log.info(res.code)
    except Exception as ex:
        gen_log.error(ex)
    IOLoop.current().add_timeout(time.time()+1,upload_telemetry_data)


@coroutine
def upload_temperature_data():
    """
    curl -v -X POST -d "{\"temperature\": 25}"
     $HOST_NAME/api/v1/$ACCESS_TOKEN/telemetry 
     --header "Content-Type:application/json"

    """
    gen_log.info("upload_temperature_data")
    try:
            
        data={"temperature":random.randint(20,100)}
        url=url_prefix+'/v1/{}/telemetry'.format(token)
        res=yield AsyncHTTPClient().fetch(url,method='POST',body=json.dumps(data),headers=headers)
        #res=requests.post(url,data=json.dumps(data),headers=headers)
        gen_log.info(res.code)
    except Exception as ex:
        gen_log.error(ex)
    IOLoop.current().add_timeout(time.time()+1,upload_temperature_data)

if __name__ == '__main__':
    parse_command_line()
    token=options.token
    if token is None:
        gen_log.error('device access token can not None')
        sys.exit(1)
    
    IOLoop.current().add_callback(upload_temperature_data)
    IOLoop.current().add_callback(upload_telemetry_data)
    IOLoop.current().add_callback(upload_attribute_data)
    IOLoop.current().start()

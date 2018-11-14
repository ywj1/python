#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import requests
import json
import xmltodict


def xml_to_json(xmlStr):
    xmlParse = xmltodict.parse(xmlStr)
    jsonStr = json.dumps(xmlParse,indent = 1)
    return jsonStr

def weatherXML(place):
    url = "http://wthrcdn.etouch.cn/WeatherApi?city={}".format(place)
    weatherText = requests.get(url).text
    return weatherText

def GetWeather(jsonStr):
    data = json.loads(jsonStr)
    date = datetime.date.today()
    city = data['resp']['city']
    shidu = data['resp']['shidu']
    wendu = data['resp']['wendu']
    quality = data['resp']['environment']['quality']
    suggest = data['resp']['environment']['suggest']
    print("{}:{},湿度：{},温度：{},空气质量{},{}".format(city,date,shidu,wendu,quality,suggest))

if __name__ == '__main__':
    GetWeather(xml_to_json(weatherXML('北京')))
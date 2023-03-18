import json
import logging

import requests
import math

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')


def get_coordinates(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': city_name,
            'format': 'json'
        }
        respose = requests.get(url, params)
        json = respose.json()
        coordinates_str = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        long, lat = map(float, coordinates_str.split())
        return long, lat
    except Exception as e:
        return e


def get_country(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': city_name,
            'format': 'json'
        }
        respose = requests.get(url, params)
        json = respose.json()
        country = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['metaDataProperty'][
            'GeocogerMetaData']['AddressDetails']['Country']['CountryName']
        return country
    except Exception as e:
        return e


def get_distance(p1, p2):
    radius = 6373
    lon1 = math.radians(p1[0])
    lat1 = math.radians(p1[1])
    lon2 = math.radians(p2[0])
    lat2 = math.radians(p2[1])
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) \
        * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)
    return radius * c


@app.route('/post', methods='POST')
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['sesion']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу показать город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if not cities:
        res['response']['text'] = 'Ты не написал название не одного города!'
    elif len(cities) == 1:
        res['response']['text'] = f'Этот город в стране - {get_country(cities[0])}.'
    elif len(cities) == 2:
        dist = get_distance(get_coordinates(cities[0]), get_coordinates(cities[1]))
        res['response']['text'] = f'Расстояние между этими городами: {round(dist)} км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for en in req['request']['nlu']['entities']:
        if en['type'] == 'YANDEX.GEO':
            if 'city' in en['value']:
                cities.append(en['value']['city'])
    return cities


if __name__ == '__main__':
    app.run()

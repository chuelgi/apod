import os
from datetime import datetime
from flask import Flask, redirect, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('ENTRY')


API_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('date.html')

@app.route('/search', methods=['GET'])
def search():
    user_date = request.args.get('date')

    legacy_date = user_date.replace("-","")[2:]

    response = requests.get(API_URL + legacy_date)
    print(response.url)
    data = response.json()
    image = data['hdurl']
    print(data['date'])

    return jsonify({'image': image})

@app.route('/all_dates', methods=['GET'])
def all_dates():
    #user birthdate
    birth_date = request.args.get('date')


    if not birth_date:
        return render_template('birthdate.html')


    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')

    today = datetime.today()
    current_year = today.year

    #calculate age, age = #of images


    images = []

    #put date in legacy date for api


    years = range(birth_date.year, current_year + 1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        images = list(executor.map(
            lambda year: get_apod(year, birth_date),
        years
        ))

    return render_template('birthday_images.html', images=images)

def get_apod(year, birth_date):
    apod = datetime(year, birth_date.month, birth_date.day)
    legacy_date = apod.strftime("%y%m%d")

    # returns dict
    response = requests.get(API_URL + legacy_date, timeout= 15)
    response.raise_for_status()

    data = response.json()

    return {'date' : data.get('date'),
            'image' : data.get('hdurl') }

if __name__ == '__main__':
    app.run(debug=True)
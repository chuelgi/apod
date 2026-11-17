import os
from datetime import datetime, date
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
    return render_template('home.html')

@app.route('/today', methods=['GET'])
def today():

    today = datetime.today()

    images = get_apod(today)
    return render_template('today.html', images=images)


@app.route('/search', methods=['GET'])
def search():

    user_date = request.args.get('date')

    if not user_date: #return todays date
        return render_template('date.html', image=None)
    else:

        date = datetime.strptime(user_date, '%Y-%m-%d')

        image = get_apod(date)

    return render_template('date.html', image=image)

@app.route('/all_dates', methods=['GET'])
def all_dates():
    #user birthdate
    birth_date = request.args.get('date')


    if not birth_date:
        return render_template('birthdate.html')


    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')

    today = datetime.today()
    current_year = today.year

    birthday_dates = []
    #calculate age, age = #of images



    #put date in legacy date for api

    years = range(birth_date.year, current_year + 1)

    for year in range(birth_date.year, current_year + 1):
        one_birthday = datetime(year, birth_date.month, birth_date.day)
        birthday_dates.append(one_birthday)

    with ThreadPoolExecutor(max_workers=10) as executor:
        images = list(executor.map(get_apod, birthday_dates))


    return render_template('birthday_images.html', images=images)

def get_apod(start_date):
    """
    takes date and returns image

    :param start_date:
    :return: dictionary with date and image
    """
    legacy_date = start_date.strftime("%y%m%d")

    # returns dict
    response = requests.get(API_URL + legacy_date, timeout= 15)
    response.raise_for_status()

    data = response.json()

    return {'date' : data.get('date'),
            'image' : data.get('hdurl') }

@app.context_processor
def inject_today():
    return {'max_date' : date.today().isoformat()}
if __name__ == '__main__':
    app.run(debug=True)
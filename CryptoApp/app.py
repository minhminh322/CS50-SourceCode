from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/')
def home():
    response = requests.get(
        'https://api.coingecko.com/api/v3/coins/markets', params={'vs_currency': 'usd'})
    crypto_data = response.json()
    return render_template('index.html', crypto_data=crypto_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    # Choose ONE method (depend on how you send the request through Search input):
    if request.method == 'GET':
        coin_name = request.args.get('coin_name')
        if coin_name:
            response = requests.get(
                f'https://api.coingecko.com/api/v3/coins/{coin_name.lower()}')
            if response.status_code == 200:
                coin_detail = response.json()
                return render_template('coin_detail.html', coin_detail=coin_detail)
            else:
                error_message = "Coin not found. Please try again."
                return render_template('search.html', error_message=error_message)
    if request.method == 'POST':
        coin_name = request.form['coin_name']
        if coin_name:
            response = requests.get(
                f'https://api.coingecko.com/api/v3/coins/{coin_name}')
            if response.status_code == 200:
                coin_detail = response.json()
                return render_template('coin_detail.html', coin_detail=coin_detail)
            else:
                error_message = "Coin not found. Please try again."
                return render_template('search.html', error_message=error_message)

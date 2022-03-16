import pandas as pd
import json
from apscheduler.schedulers.background import BackgroundScheduler
from bokeh.embed import components
from flask import Flask, render_template, abort
from flask_caching import Cache

from src.data import (request_historical_data, request_live_data, delta_time, read_data, path_live, path_log_live,
                      path_historical, path_log_historical)
from src.visualization import country_graph, world_graph


with open('config.json') as config_file:
    config = json.load(config_file)

sched = BackgroundScheduler(daemon=True)
sched.add_job(request_live_data, 'interval', seconds=300)
sched.add_job(request_historical_data, 'interval', seconds=1800)
sched.start()

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
app.config['SECRET_KEY'] = config.get('SECRET_KEY', 'change-in-production')
cache.init_app(app)


@cache.cached(timeout=450, key_prefix='live_data')
def get_live_data(path_data, path_log):
    try:
        df, update_time = read_data(path_data, path_log)
    except FileNotFoundError:
        request_live_data()
        df, update_time = read_data(path_data, path_log)
    return df, update_time


@cache.cached(timeout=2000, key_prefix='historical_data')
def get_historical_data(path_data, path_log):
    try:
        df, update_time = read_data(path_data, path_log)
    except FileNotFoundError:
        request_historical_data()
        df, update_time = read_data(path_data, path_log)
    df['dateRep'] = pd.to_datetime(df['dateRep'], dayfirst=True)
    df.sort_values('dateRep', ascending=True, inplace=True)
    return df, update_time


@app.errorhandler(403)
def error_404(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def error_404(error):
    return render_template('errors/500.html'), 500


@app.route('/')
@cache.cached(timeout=400)
def home():
    historical_data, _ = get_historical_data(
        path_historical, path_log_historical)
    pDWorld = world_graph(historical_data, x='dateRep', y='deaths', color_bar='indianred',
                          color_line='red')
    pCWorld = world_graph(historical_data, x='dateRep', y='cases', color_bar='royalblue',
                          color_line='dodgerblue')
    scriptDWorld, divDWorld = components(pDWorld)
    scriptCWorld, divCWorld = components(pCWorld)
    live_data, update_time = get_live_data(path_live, path_log_live)
    live_data = live_data.to_dict('records')
    last_update = delta_time(update_time)
    return render_template('home.html', data=live_data, last_update=last_update, scriptDWorld=scriptDWorld,
                           divDWorld=divDWorld,
                           scriptCWorld=scriptCWorld, divCWorld=divCWorld)


@app.route("/country/<string:country_code>")
def country(country_code):
    live_data, _ = get_live_data(path_live, path_log_live)
    live_data = live_data.to_dict('records')

    for location in live_data:
        if location['CountryCode'] == country_code:
            country_data = location
            break
    else:
        abort(404)

    historical_data, _ = get_historical_data(
        path_historical, path_log_historical)

    try:
        historical_data = historical_data[historical_data['countryterritoryCode'] == country_code]
    except:  # Si no encuentra el país en los datos, error 404. TODO: añadir causa al except
        abort(404)

    historical_data['deathsMovingAverage'] = historical_data['deaths'].rolling(
        window=7).mean()
    historical_data['casesMovingAverage'] = historical_data['cases'].rolling(
        window=7).mean()
    historical_data['deathsAccum'] = historical_data['deaths'].cumsum()
    historical_data['casesAccum'] = historical_data['cases'].cumsum()
    historical_data['deathsChange'] = historical_data['deathsAccum'].pct_change(
    ) * 100
    historical_data['casesChange'] = historical_data['casesAccum'].pct_change() * \
        100
    historical_data.fillna(0, inplace=True)
    pD1, pA1 = country_graph(historical_data, countryCode=country_code, x='dateRep', y='deaths', color_bar='indianred',
                             color_line='red')
    pD2, pA2 = country_graph(historical_data, countryCode=country_code, x='dateRep', y='cases', color_bar='royalblue',
                             color_line='dodgerblue')
    scriptD1, divD1 = components(pD1)
    scriptA1, divA1 = components(pA1)
    scriptD2, divD2 = components(pD2)
    scriptA2, divA2 = components(pA2)

    historical_data.sort_values('dateRep', ascending=False, inplace=True)
    historical_data = historical_data.to_dict('records')

    return render_template('country.html', data=country_data, historical_data=historical_data,
                           script1=scriptD1, div1=divD1,
                           script2=scriptA1, div2=divA1,
                           script3=scriptD2, div3=divD2, script4=scriptA2, div4=divA2)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)

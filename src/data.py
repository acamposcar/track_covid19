import datetime

import pandas as pd
import requests

path_live = './data/live_data.csv'
path_log_live = './data/log_live_data.txt'
path_historical = './data/historical_data.csv'
path_log_historical = './data/log_historical_data.txt'


def read_data(path_data, path_log):
    df = pd.read_csv(path_data)

    with open(path_log) as f:
        update_time = f.readline()
        update_time = datetime.datetime.strptime(update_time, "%Y-%B-%d %H:%M:%S")

    return df, update_time


def save_data(df, update_time, path_data, path_log):
    df.to_csv(path_data, index=False)

    with open(path_log, 'w') as f:
        f.write(update_time.strftime("%Y-%B-%d %H:%M:%S"))


def clean_live_data(df):
    # Read Country ISO Codes
    codes = pd.read_csv('./data/country_codes.csv', index_col=0).to_dict()
    # Clean Data
    df.rename(columns={'Country,Other': 'Country', 'Serious,Critical': 'Critical'}, inplace=True)
    df["CountryCode"] = df['Country'].map(codes['ISO3'])
    df["CountryName"] = df['Country'].map(codes['CountryName'])
    df["Population"] = df['Country'].map(codes['Population'])
    df['DeathsPop'] = df['TotalDeaths'] * 100_000 // df["Population"]
    df['DeathsPop'] = df['DeathsPop'].fillna(0).astype(int)
    df['DeathsPop'] = df['DeathsPop'].apply(lambda x: "<1" if x == 0 else x)

    df['CasesPop'] = df['TotalCases'] * 100_000 // df["Population"]
    df['CasesPop'] = df['CasesPop'].fillna(0).astype(int)
    df['CasesPop'] = df['CasesPop'].apply(lambda x: "<1" if x == 0 else x)

    df.fillna(0, inplace=True)
    df.sort_values('TotalDeaths', ascending=False, inplace=True)
    df = df[df['Country'] != 'Total:']  # Remove Total row

    return df


def request_live_data():
    try:
        r = requests.get('https://www.worldometers.info/coronavirus/',
                         headers={'User-agent': 'Mozilla/5.0'}, timeout=10)
    except requests.exceptions.ReadTimeout:
        return

    if r.status_code == requests.codes.ok:
        df = pd.read_html(r.text)[0]
        df = clean_live_data(df)
        update_time = datetime.datetime.now()
        save_data(df, update_time, path_live, path_log_live)


def request_historical_data():
    url_data = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
    try:
        r = requests.get(url_data, headers={'User-agent': 'Mozilla/5.0'}, timeout=10)
    except requests.exceptions.ReadTimeout:
        return

    if r.status_code == requests.codes.ok:
        df = pd.read_csv(url_data)
        update_time = datetime.datetime.now()
        save_data(df, update_time, path_historical, path_log_historical)


def delta_time(update_time):
    delta = (datetime.datetime.now() - update_time).seconds // 60

    if delta < 2:
        return "a few seconds ago"
    elif 60 <= delta < 120:
        return str(delta // 60) + ' hour ago'
    elif delta >= 120:
        return str(delta // 60) + ' hours ago'
    else:
        return str(delta) + ' minutes ago'

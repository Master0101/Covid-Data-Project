import requests as request
import requests
import json as js
from pandas import json_normalize
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session.__init__  import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def normal():
    return render_template("blank.html")

@app.route("/", methods = ["POST","GET"])
def image():
    country = request.form["country"]
    
    #GRAPH
    request1 = requests.get(f'https://api.covid19api.com/dayone/country/{country}/status/confirmed')

    if not request1:
        return render_template("error.html")
    
    request1 = js.loads(request1.content)

    df = json_normalize(request1)

    df = pd.DataFrame(df)

    del df["CountryCode"]
    del df["Province"]
    del df["City"]
    del df["CityCode"]
    del df["Lat"]
    del df["Lon"]
    del df["Status"]

    df["Date"] = pd.to_datetime(df['Date']).dt.date
    x = df.Date
    y = df.Cases

    fig, ax = plt.subplots(figsize = (15,15))

    ax.grid()

    ax.set_ylim([-(float(df["Cases"].max())*0.1),(float(df["Cases"].max())*1.1)])

    ax.set_xlabel('Date', fontsize = 'large')
    ax.set_ylabel('Cases', fontsize = 'large')
    ax.set(title = country)

    ax.plot(x,y)

    plt.savefig("static/test.png")
    
    #Numbers
    request1 = requests.get(f'https://api.covid19api.com/total/country/{country}')

    if request1.status_code != 200:
        sys.exit(1)
    
    request1 = js.loads(request1.content)

    df = json_normalize(request1)

    df = pd.DataFrame(df)

    hack = len(df.index)
    
    df = df.tail(2)

    del df["CountryCode"]
    del df["Province"]
    del df["City"]
    del df["CityCode"]
    del df["Lat"]
    del df["Lon"]
    
    new_cases = df.at[(hack-1),'Confirmed'] - df.at[(hack-2),'Confirmed']
    total_cases = df.at[(hack - 1), 'Confirmed']
    new_deaths = df.at[(hack-1),'Deaths'] - df.at[(hack-2),'Deaths']
    total_deaths = df.at[(hack-1), 'Deaths']
    total_recovered = df.at[(hack-1),'Recovered']
    total_active = df.at[(hack-1),'Active']
    return render_template("blank2.html", nc = new_cases, tc = total_cases, nd = new_deaths, td = total_deaths, tr = total_recovered, ta = total_active, c = country)
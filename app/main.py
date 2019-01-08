from flask import Flask, render_template, request, Response, send_file, jsonify
from flask import render_template_string
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ephem
import datetime
import pytz
import subprocess

app = Flask(__name__)


def send_email(formdata):

    email_cmds = ["mail",
                  "-s",
                  "Nightly Report",
                  "-a",
                  "Content-Type: text/html; charset=UTF-8",
                  "srswinde@gmail.com"]
    subprocess.run(email_cmds, input="<h1>nightreport</h1>")


@app.route("/")
def home():
    return "ROOT"


@app.route("/fool", methods=['GET', 'POST'])
def send_nr():
    formdata = {}
    for key, value in request.form.items():
        if type(value) == list:
            formdata[key] = value[0]
        else:
            formdata[key] = value
    send_email(formdata)
    return render_template("submitted_report.html", **formdata)




@app.route( "/nr", methods=['GET', 'POST'] )
def night_report():

    conf = json.loads(open("nightly_report.json").read())
    ip_addr = request.remote_addr
    if ip_addr not in conf["ip2obs"]:
        observatory = conf["observatories"]["tucson"]
    ephem_obs = ephem.Observer()
    ephem_obs.lat = observatory["lat"]
    ephem_obs.lon = observatory["lon"]
    sun = ephem.Sun()

    now = datetime.datetime.now(pytz.timezone("America/Phoenix"))
    if now.hour > 12:  # after 12:00 use next midnight
        midnight = datetime.datetime(
            now.year,
            now.month,
            now.day+1,
            12,
            0,
            0
        )

    else:  # befoore noon use previous midnight
        midnight = datetime.datetime(
            now.year,
            now.month,
            now.day,
            12,
            0,
            0
        )

    ephem_obs.date = midnight
    sun.compute(ephem_obs)

    avail_hours = (sun.rise_time - sun.set_time)*24
    return render_template(
        "nightly_report.html",
        TEL_ID=request.remote_addr,
        moon_age="{:4.1f}".format(moon_age()),
        date=str(datetime.datetime.utcnow().ctime()),
        avail_hours="{:4.1f}".format(avail_hours)
    )


def moon_age(now=None):
    if now is None:
        now = ephem.now()
    pmoon = ephem.previous_new_moon(now)
    nmoon = ephem.next_new_moon(now)
    deltamoon = nmoon - pmoon
    since_new = now - ephem.previous_new_moon(now)
    till_new = now - ephem.next_new_moon(now)
    print(since_new, deltamoon/2.0)
    if since_new > deltamoon/2.0:
        age = till_new
    else:
        age = since_new


    return age


@app.route("/js")
def js():
    return render_template("do.js")


if __name__ == "__main__":
    app.run( host="0.0.0.0", port=8888 )


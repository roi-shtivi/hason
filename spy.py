#!/usr/bin/env python3

import os
import smtplib
from datetime import datetime
from contextlib import closing
from requests import get

from requests.exceptions import RequestException
from bs4 import BeautifulSoup

SHOWS_URL = 'http://www.comedybar.co.il/show.php?id=52'
USER_ENV_VAR = 'hason_email_user_name'
PASS_ENV_VAR = 'hason_email_password'
EPOCH = datetime(1, 1, 1, 0, 0)


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def get_date():
    """
    Get the latest show date that is already known and saved in date.txt file,
    if no such file is exist, return the date of epoch.
    """
    latest_known_show_date = EPOCH
    try:
        with open("date.txt", "r") as f:
            str_file_time = f.read()
            file_date = datetime.strptime(str_file_time, '%d/%m/%Y')
            latest_known_show_date = file_date if file_date > latest_known_show_date else latest_known_show_date
    except IOError:
        pass
    return latest_known_show_date


def set_date(date):
    """Write 'date' in '%d/%m/%Y' format in date.txt file"""
    try:
        with open("date.txt", "w") as f:
            f.write(datetime.strftime(date, '%d/%m/%Y'))
    except IOError:
        pass


def check_new_shows():
    """Check whether new shows of Shahar Hason is published"""
    raw_html = simple_get(SHOWS_URL)

    if raw_html is None:
        print('Could not get url')
        return None

    html = BeautifulSoup(raw_html, 'html.parser')
    shows_date_containers = html.select(".show_appearances_list_field_content_date")
    dates = [datetime.strptime(d.contents[0], '%d/%m/%Y') for d in shows_date_containers]
    known_date = get_date()
    max_date = max(dates)
    if max_date > known_date:
        set_date(max_date)
        if known_date != EPOCH:
            return True
    return False


def get_mail_information():
    """Retrieve the sender mail user name and password that are set locally with environment variables"""
    try:
        user = os.environ[USER_ENV_VAR]
        password = os.environ[PASS_ENV_VAR]
        return user, password
    except Exception:
        print("Could not retrieve sender mail information."
              " Please make sure your environment variable are set correctly.")
        return None


def notify():
    """Send an email"""
    server = smtplib.SMTP('mail.shtivi.xyz:587')
    server.ehlo()
    server.starttls()
    info = get_mail_information()
    if info is None:
        return
    user, password = info
    server.login(user, password)
    receivers = ["roi@shtivi.xyz"]
    msg = "\r\n".join([
        "From: {}".format(user),
        "To: {}".format(" ".join(receivers)),
        "Subject: New Shahar Hason show is open!",
        "",
        "You can book a ticket here: {}".format(SHOWS_URL)
    ])
    server.sendmail(user, receivers, msg)
    server.close()


if __name__ == '__main__':
    if check_new_shows():
        notify()

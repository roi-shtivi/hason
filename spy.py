from bs4 import BeautifulSoup
from contextlib import closing
from requests import get
from requests.exceptions import RequestException
from datetime import datetime


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
    latest_known_show_date = datetime(1, 1, 1, 0, 0)
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
    url = 'http://www.comedybar.co.il/show.php?id=52'
    raw_html = simple_get(url)

    if raw_html is None:
        print('Could not get url')
        return None

    html = BeautifulSoup(raw_html, 'html.parser')
    shows_date_containers = html.select(".show_appearances_list_field_content_date")
    dates = [datetime.strptime(d.contents[0], '%d/%m/%Y') for d in shows_date_containers]
    max_date = max(dates)
    if max_date > get_date():
        set_date(max_date)
        return True
    return False


def notify():
    pass


if __name__ == '__main__':
    # if check_new_shows():
    notify()

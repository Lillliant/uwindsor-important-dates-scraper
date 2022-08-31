from bs4 import BeautifulSoup
from collections import defaultdict
import datetime
import json
import urllib.request

def update_url(index, url):
    ext = ["", "?page=1", "?page=2", "?page=3", "?page=4", "?page=5"]
    return url + ext[index]

def retrieve_soup(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(), "html.parser")
    page.close()
    return soup

def get_start_date(date):
    end_index = date.index(" to ")
    return date[:end_index]

def get_end_date(date):
    start_index = date.index(" to ") + 4
    return date[start_index:]

def date_id(date):
    months = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
    day = date.split(" to ")[0]
    tmp = day.replace(day[:3], months.get(day[:3])) # replace the months with numbers
    numeric_filter = filter(str.isdigit, tmp)
    tmp = "".join(numeric_filter) # remove all characters that are not numbers

    if len(tmp) == 7:
        day = tmp[0:2] + "0" + tmp[2:] # for singular days (ex. 9th), add a 0 for format consistency
    else:
        day = tmp

    return day

def strip_extra(str):
    return str.replace(".", "").replace("\u2026","")

page_url = "https://www.uwindsor.ca/registrar/events-listing"
important_dates = defaultdict(list)

out_filename = "dates.txt"
f = open(out_filename, "w") # write to a txt file for reference

def get_academic_dates(dates, url):
    for i in range(6):
        soup = retrieve_soup(update_url(i, url))
        events = soup.findAll("tr", {"class" : ["odd views-row-first", "odd", "even"]})
        
        for event in events:
            event_info = {}
            date = event.find_all("td", {"class": "views-field views-field-field-event-date event-listing-date"})[0].text.strip() #grabs attributes
            event_info["date"] = date
            event_info["eventname"] = strip_extra(event.find_all("td", {"class": "views-field views-field-title"})[0].text.strip())
            
            f.write(date + " : " + event_info["eventname"] + "\n") # writes to txt

            important_dates[date_id(date)].append(event_info)
    
    return dates


get_academic_dates(important_dates, page_url)

f.close() # close txt file

fp = open("important_dates.json", "w") # write 
json.dump(important_dates, fp, indent=4)
fp.close()

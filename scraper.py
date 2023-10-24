from bs4 import BeautifulSoup
from collections import defaultdict
import json
import urllib.request

academic_url = "https://www.uwindsor.ca/registrar/events-listing"
financial_url = "https://www.uwindsor.ca/studentawards/425/financial-aid-important-dates"
important_dates = defaultdict(list) # for writing to JSON file
filtered_dates = defaultdict(list) # for writing to JSON file

f = open("dates.txt", "w") # write to a txt file for reference

def update_url(index, url):
    ext = ["", "?page=1", "?page=2", "?page=3", "?page=4", "?page=5"]
    return url + ext[index]

def retrieve_soup(url):
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(), "html.parser")
    page.close()
    return soup

def format_id(raw):
    if len(raw) == 7:
        id = raw[3:] + raw[0:2] + "0" + raw[2] # for singular days (ex. 9th), add a 0 for format consistency
    else:
        id = raw[4:] + raw[0:4]
    
    return id

def id_for_short_date(date):
    months = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
    day = date.split(" to ")[0]
    day = day.replace(day[:3], months.get(day[:3])) # replace the months with numbers
    numeric_filter = filter(str.isdigit, day)
    day = "".join(numeric_filter) # remove all characters that are not numbers

    return format_id(day)

def id_for_long_date(date):
    months = {"January":"01", "February":"02", "March":"03", "April":"04", "May":"05", "June":"06", "July":"07", "August":"08", "September":"09", "October":"10", "November":"11", "December":"12"}
    day = date.split(" to ")[0]

    for month in months.keys():
        if date.find(month) != -1:
            end_index = len(month)
            day = day.replace(day[:end_index], months.get(month))
            break

    numeric_filter = filter(str.isdigit, day)
    day = "".join(numeric_filter) # remove all characters that are not numbers

    return format_id(day)

def strip_extra(str):
    to_strip = [".", "\u2026", "\u00a0"]
    for c in to_strip:
        str = str.replace(c, "")
    return str

def get_academic_dates(url):
    for i in range(6):
        soup = retrieve_soup(update_url(i, url))
        events = soup.findAll("tr", {"class" : ["odd views-row-first", "odd", "even"]})
        
        for event in events:
            event_info = {}
            date = event.find_all("td", {"class": "views-field views-field-field-event-date event-listing-date"})[0].text.strip() #grabs attributes
            event_info["date"] = date
            event_info["eventname"] = strip_extra(event.find_all("td", {"class": "views-field views-field-title"})[0].text.strip())
            
            f.write(date + " : " + event_info["eventname"] + "\n") # writes to txt

            if is_general_undergrad_event(event_info["eventname"]):
                important_dates[id_for_short_date(date)].append(event_info)

def get_financial_dates(url):
    soup = retrieve_soup(url)
    events = soup.findAll("tbody")[0].find_all("tr")[1:]

    for event in events:
        event_info = {}
        raw = event.find_all("td") #grabs attributes
        date = raw[0].text.strip() 

        event_info["date"] = date
        event_info["eventname"] = strip_extra(raw[1].text.strip())

        f.write(date + " : " + event_info["eventname"] + "\n") # writes to txt

        if is_general_undergrad_event(event_info["eventname"]):
            important_dates[id_for_long_date(date)].append(event_info)

def is_general_undergrad_event(event_name):
    if not (event_name.find("nursing") != -1 or event_name.find("grad:") != -1 or event_name.find("concurrent ed:") != -1 or event_name.find("consecutive ed:") != -1 or event_name.find("law:") != -1):
        return True
    elif event_name.find("law") and not (event_name.find("excluding") or event_name.find("except")):
        return True
    else:
        return False

def find_semester_term(str):
    if str.find("fall") ==  True:
        return "Fall"
    elif str.find("winter") == True:
        return "Winter"
    elif str.find("summer") == True:
        return "summer"

def organize_by_semester():
    semester_events = {}
    semester_term = ""
    for date in important_dates:
        semester_start = False
        for event in date:
            event_name = event.get("eventname").lowercase().find("first day")
            if event_name != -1:
                semester_start = True
                semester_term = find_semester_term(event_name) + " " + event_name.findall("20[0-9][0-9]") # this will be good for a while (until year 2100)
                break
            
        if semester_start != True:
            semester_events.append(date)
        else:
            semester_events.append(date)
            filtered_dates[semester_term].append(semester_events)
            print("hi")

#the start of scraping
get_academic_dates(academic_url)
get_financial_dates(financial_url)
# organize_by_semester()

f.close() # close txt file

fp = open("important_dates.json", "w") # write to JSON
json.dump(important_dates, fp, indent=4)
fp.close()

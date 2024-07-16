import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from flask import Flask, request, jsonify
import schedule
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import sys
import logging


def daily_task():
    global all_movie_run_times
    global movie_showings
    global fresh_data_scheduler
    if fresh_data_scheduler.running:
        fresh_data_scheduler.remove_all_jobs()
        fresh_data_scheduler.shutdown()
    all_movie_run_times = get_all_movies_with_runtime()
    movie_showings = asyncio.run(get_all_movie_showings(all_movie_run_times))
    for showing in movie_showings:
        formatted_time = parse_and_format_time(showing[4])
        hour, minute = map(int, formatted_time.split(':'))
        app.logger.info(formatted_time, file=sys.stderr)
        app.logger.info(hour, file=sys.stderr)
        app.logger.info(minute, file=sys.stderr)
        app.logger.info(showing[2], file=sys.stderr)
        fresh_data_scheduler.add_job(func = update_movie, trigger='cron',args=(showing[2],), hour=hour, minute=minute)
    fresh_data_scheduler.start()



all_movie_run_times=defaultdict(list)
movie_showings=[]
daily_scheduler:BackgroundScheduler = BackgroundScheduler()
fresh_data_scheduler:BackgroundScheduler  = BackgroundScheduler()
daily_scheduler_initialized = False

# Fetch the HTML content

target_theatre_url= "https://www.cinemark.com/theatres/ca-los-angeles/cinemark-howard-hughes-los-angeles-and-xd"
main_movie_url ="https://www.cinemark.com"
# response = requests.get(main_movie_url+"/movies/now-playing")
#response = requests.get(target_theatre_url)

def default_arr():
    return [0, 0]
def default_tuple():
    return ()
    
def get_movie_name(elements):
    has_name_started=False
    has_name_ended=False
    movie_name=""
    for element in elements:
        for char in str(element):
            if has_name_started and char=='<':
                has_name_ended = True
            if has_name_started==True and has_name_ended==False:
                movie_name+=char
            if char=='>':
                has_name_started=True
            if has_name_ended:
                return movie_name
    return movie_name
def get_movie_hours_minutes(elements):
    nums=[]
    numsString=""
    lastCharIsDigit=False
    for element in elements:
        for char in str(element):
            if char.isdigit()==False and lastCharIsDigit==True:
                nums.append(int(numsString))
                numsString=""
                lastCharIsDigit=False
            if char.isdigit():
                numsString+=char
                lastCharIsDigit=True
    return nums
def get_all_movies_with_runtime():
    response = requests.get(main_movie_url+"/movies/now-playing")
    movie_runtime_dict = defaultdict(default_arr)
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}", file=sys.stderr)
        return movie_runtime_dict
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    anchor_tags = soup.find_all('a', class_="movie-poster")
    hrefs = [a.get('href') for a in anchor_tags if a.get('href')]
    # limit =4
    for movie_link in hrefs:
        response = requests.get(main_movie_url+str(movie_link))
        if response.status_code == 200:
            html_content = response.text
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            movie_name_element = soup.find_all(class_='movie-detail-title')
            movie_name= get_movie_name(movie_name_element)
            app.logger.info(movie_name, file=sys.stderr)
            # Extract elements with a specific class
            movie_runtime_element = soup.find_all(class_='movie-detail-runtime')
            hours_minutes = get_movie_hours_minutes(movie_runtime_element)
            movie_runtime_dict[movie_name]=hours_minutes
        else:
            app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}", file=sys.stderr)
        # if limit<=0:
        #     break
        # limit-=1
    return movie_runtime_dict
def get_all_movie_start_times():
    response = requests.get(target_theatre_url)
    movies_playing_dict =defaultdict(list)
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}", file=sys.stderr)
        return movies_playing_dict
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    movies_playing_today_elements= soup.find_all(class_='showtimeMovie')
    movie_name=""
    movie_start_times =[]
    for movie_element in movies_playing_today_elements:
        movie_name = movie_element.find('h3').text.strip()
        times =movie_element.find_all(class_='showtime-link')
        #   app.logger.info(movie_name)
        for time in times:
            movie_start_times.append(str(time.text.strip()))
            #   app.logger.info(time.text.strip())
        movies_playing_dict[str(movie_name)] = movie_start_times
        movie_start_times =[]
    return movies_playing_dict
        
#start_time:str, duration:list
def calculate_end_time(start_time_str:str, runtime:list):
    # start_time_str = "11:15 am"
    # runtime = [2, 30]  # 2 hours and 30 minutes

    # Step 1: Parse the start time string into a datetime object
    start_time = datetime.strptime(start_time_str, "%I:%M %p")

    # Step 2: Create a timedelta object for the runtime
    runtime_delta = timedelta(hours=runtime[0], minutes=runtime[1])

    # Step 3: Calculate the end time by adding the runtime to the start time
    end_time = start_time + runtime_delta

    # Step 4: Format the end time as a string if needed
    end_time_str = end_time.strftime("%I:%M %p")

    app.logger.info("Start Time:", start_time_str, file=sys.stderr)
    app.logger.info("Runtime:", runtime[0], "hours and", runtime[1], "minutes", file=sys.stderr)
    app.logger.info("End Time:", end_time_str, file=sys.stderr)
    return end_time_str


def get_auditorium_details(path:str,movie_run_times: defaultdict[str, list[int]]):
    response = requests.get(main_movie_url+path)
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}", file=sys.stderr)
        return ['','query failed',path,0,"01:00 AM",[0,0],'01:00 AM']
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    movie_name=""
    auditorium_number="query failed"
    start_time = "01:00"
    run_time =[0,0]
    end_time = '01:00 AM'
    seats_unavailable = 0
    try:
        movie_name = str(soup.find(class_='seats-tickets-title').text.strip())
    except:
        app.logger.info("getting movie name failed", file=sys.stderr)
    try:
        auditorium_number= str(soup.find(class_='auditoriumNumber').text.strip())
    except:
        app.logger.info("getting auditorium number failed", file=sys.stderr)
    try:
        start_time = str(soup.find(class_='seats-tickets-time').text.strip())
        run_time =movie_run_times[movie_name]
        end_time = calculate_end_time(start_time,run_time)
    except:
        app.logger.info("getting times failed", file=sys.stderr)
    try:
        seat_map = soup.find(class_='seatMap')
        seats_unavailable = len(seat_map.find_all(class_='seatUnavailable seatBlock'))
    except:
        app.logger.info("getting seats failed", file=sys.stderr)
    app.logger.info(start_time, file=sys.stderr)
    app.logger.info(movie_name, file=sys.stderr)
    app.logger.info(auditorium_number, file=sys.stderr)
    app.logger.info(seats_unavailable, file=sys.stderr)
    return [movie_name,auditorium_number,path,seats_unavailable,start_time,run_time,end_time]

def update_movie(path):
    global movie_showings
    latest_movie_showing_details = get_auditorium_details(path,all_movie_run_times)
    for i in range(len(movie_showings)):
        if movie_showings[i][2]==path:
            app.logger.info(movie_showings[i], file=sys.stderr)
            app.logger.info('updating latest', file=sys.stderr)
            app.logger.info(latest_movie_showing_details, file=sys.stderr)
            for j in range(len(movie_showings[i])):
                movie_showings[i][j]=latest_movie_showing_details[j]
    return latest_movie_showing_details

def convert_time_to_datetime(time_str):
    return datetime.strptime(time_str, "%I:%M %p")
def parse_and_format_time(input_time, output_format="%H:%M"):
    # Parse the input time string
    dt = datetime.strptime(input_time, "%I:%M %p")
    
    # Format the datetime object to the desired format
    formatted_time = dt.strftime(output_format)
    
    return formatted_time

async def get_all_movie_showings(all_movie_run_times: dict[str, list[int]]):
    response = requests.get(target_theatre_url)
    movies = []
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}", file=sys.stderr)
        return movies
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    anchor_tags = soup.find_all(class_='showtime-link')
    hrefs = [a.get('href') for a in anchor_tags if a.get('href')]
    # limit = 2
    for showtime_path in hrefs:
        path= str(showtime_path)
        auditorium= get_auditorium_details(path,all_movie_run_times)
        movies.append(auditorium)
        await asyncio.sleep(10)
        # if limit<=0:
        #     break
        # limit-=1
    sorted_times_list = sorted(movies, key=lambda x: convert_time_to_datetime(x[6]))
    app.logger.info(sorted_times_list, file=sys.stderr)
    return sorted_times_list



# --------app schedulers -------





#-------end app schedulers ----------

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# Define a route for the default URL, which loads the homepage
@app.route('/')
def home():
    return "Welcome to the Flask API!"

# Define a route for an example API endpoint
@app.route('/api/data', methods=['GET'])
def get_all_movie_run_times():
    # Example data
    global movie_showings
    formatted_movies = []
    for movie in movie_showings:
        details ={
            'movie_name':movie[0],
            'auditorium_number':movie[1],
            'url':movie[2],
            'seats_unavailable':movie[3],
            'start_time':movie[4],
            'run_time':movie[5],
            'end_time':movie[6]
        }
        formatted_movies.append(details)
    data = {
        'message': formatted_movies,
        'status': 'success'
    }
    return jsonify(data)

#Define a route for an API endpoint with parameters
@app.route('/api/start/schedules', methods=['GET'])
def get_data_with_name():
    global daily_scheduler
    job_count = len(daily_scheduler.get_jobs())
    if job_count==0:
        daily_scheduler.add_job(daily_task, CronTrigger(hour=20, minute=15))
        daily_scheduler.start()
    return "hello"

@app.route('/api/get_latest', methods=['GET'])
def get_latest_auditorium_details():
    path = request.args.get('path')
    latest_movie_showing_details = update_movie(path)

    data = {
        'message':{
            'movie_name':latest_movie_showing_details[0],
            'auditorium_number':latest_movie_showing_details[1],
            'url':latest_movie_showing_details[2],
            'seats_unavailable':latest_movie_showing_details[3],
            'start_time':latest_movie_showing_details[4],
            'run_time':latest_movie_showing_details[5],
            'end_time':latest_movie_showing_details[6]
        }
        ,
        'status': 'success'
    }
    return jsonify(data)

# Run the app
if __name__ == '__main__':
    try:
        daily_task()
        app.run(port=8000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        daily_scheduler.shutdown()
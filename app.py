import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import gc



all_movie_run_times=defaultdict(list)
movie_showings=[{"auditorium_number":"Auditorium 5","end_time":"12:18 AM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":16,"start_time":"9:45 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=369054&CinemarkMovieId=97171&Showtime=2024-07-30T21:45:00"},{"auditorium_number":"Auditorium 6","end_time":"12:37 AM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":2,"start_time":"10:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368948&CinemarkMovieId=96525&Showtime=2024-07-30T22:10:00"},{"auditorium_number":"Auditorium 11","end_time":"12:48 AM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":8,"start_time":"10:15 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364098&CinemarkMovieId=97171&Showtime=2024-07-30T22:15:00&LinkedShowtimeId=364107"},{"auditorium_number":"Auditorium 8","end_time":"01:08 AM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":0,"start_time":"10:35 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368011&CinemarkMovieId=97171&Showtime=2024-07-30T22:35:00"},{"auditorium_number":"Auditorium 3","end_time":"01:15 AM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":0,"start_time":"11:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368933&CinemarkMovieId=96521&Showtime=2024-07-30T23:10:00"},{"auditorium_number":"Auditorium 2","end_time":"01:31 AM","movie_name":"Longlegs","run_time":[1,41],"seats_unavailable":2,"start_time":"11:25 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368952&CinemarkMovieId=96524&Showtime=2024-07-30T23:25:00"},{"auditorium_number":"Auditorium XD","end_time":"01:33 AM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":17,"start_time":"11:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364103&CinemarkMovieId=97171&Showtime=2024-07-30T23:00:00"},{"auditorium_number":"Auditorium 7","end_time":"01:58 AM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":5,"start_time":"11:25 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368007&CinemarkMovieId=97171&Showtime=2024-07-30T23:25:00"},{"auditorium_number":"Auditorium 4","end_time":"11:40 AM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":9,"start_time":"9:40 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368934&CinemarkMovieId=96523&Showtime=2024-07-30T09:40:00"},{"auditorium_number":"Auditorium 3","end_time":"11:46 AM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":0,"start_time":"9:45 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368949&CinemarkMovieId=96520&Showtime=2024-07-30T09:45:00"},{"auditorium_number":"Auditorium 11","end_time":"12:00 PM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":32,"start_time":"9:55 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368951&CinemarkMovieId=96521&Showtime=2024-07-30T09:55:00"},{"auditorium_number":"Auditorium 8","end_time":"12:13 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":24,"start_time":"9:40 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368950&CinemarkMovieId=97171&Showtime=2024-07-30T09:40:00"},{"auditorium_number":"Auditorium 2","end_time":"12:26 PM","movie_name":"Longlegs","run_time":[1,41],"seats_unavailable":1,"start_time":"10:20 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368928&CinemarkMovieId=96524&Showtime=2024-07-30T10:20:00"},{"auditorium_number":"Auditorium 6","end_time":"12:32 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":9,"start_time":"10:05 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368944&CinemarkMovieId=96525&Showtime=2024-07-30T10:05:00"},{"auditorium_number":"Auditorium XD","end_time":"12:33 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":15,"start_time":"10:00 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364099&CinemarkMovieId=97171&Showtime=2024-07-30T10:00:00"},{"auditorium_number":"Auditorium 1","end_time":"12:35 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":15,"start_time":"10:35 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368921&CinemarkMovieId=96523&Showtime=2024-07-30T10:35:00"},{"auditorium_number":"Auditorium 5","end_time":"12:51 PM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":7,"start_time":"10:50 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368939&CinemarkMovieId=96520&Showtime=2024-07-30T10:50:00"},{"auditorium_number":"Auditorium 7","end_time":"12:58 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":7,"start_time":"10:25 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=367999&CinemarkMovieId=97171&Showtime=2024-07-30T10:25:00"},{"auditorium_number":"Auditorium 10","end_time":"01:18 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":13,"start_time":"10:45 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364091&CinemarkMovieId=97171&Showtime=2024-07-30T10:45:00&LinkedShowtimeId=364108"},{"auditorium_number":"Auditorium 9","end_time":"01:48 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":58,"start_time":"11:15 AM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368001&CinemarkMovieId=97171&Showtime=2024-07-30T11:15:00"},{"auditorium_number":"Auditorium 4","end_time":"02:15 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":7,"start_time":"12:15 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368935&CinemarkMovieId=96523&Showtime=2024-07-30T12:15:00"},{"auditorium_number":"Auditorium 3","end_time":"02:25 PM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":7,"start_time":"12:20 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368929&CinemarkMovieId=96521&Showtime=2024-07-30T12:20:00"},{"auditorium_number":"Auditorium 2","end_time":"03:00 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":14,"start_time":"1:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368924&CinemarkMovieId=96523&Showtime=2024-07-30T13:00:00"},{"auditorium_number":"Auditorium 11","end_time":"03:08 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":42,"start_time":"12:35 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364095&CinemarkMovieId=97171&Showtime=2024-07-30T12:35:00&LinkedShowtimeId=364104"},{"auditorium_number":"Auditorium 1","end_time":"03:16 PM","movie_name":"Longlegs","run_time":[1,41],"seats_unavailable":14,"start_time":"1:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368922&CinemarkMovieId=96524&Showtime=2024-07-30T13:10:00"},{"auditorium_number":"Auditorium 8","end_time":"03:23 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":45,"start_time":"12:50 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368010&CinemarkMovieId=97171&Showtime=2024-07-30T12:50:00"},{"auditorium_number":"Auditorium 5","end_time":"03:26 PM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":12,"start_time":"1:25 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368940&CinemarkMovieId=96520&Showtime=2024-07-30T13:25:00"},{"auditorium_number":"Auditorium 6","end_time":"03:32 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":15,"start_time":"1:05 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368945&CinemarkMovieId=96525&Showtime=2024-07-30T13:05:00"},{"auditorium_number":"Auditorium XD","end_time":"03:48 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":32,"start_time":"1:15 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364100&CinemarkMovieId=97171&Showtime=2024-07-30T13:15:00"},{"auditorium_number":"Auditorium 7","end_time":"04:13 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":64,"start_time":"1:40 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368005&CinemarkMovieId=97171&Showtime=2024-07-30T13:40:00"},{"auditorium_number":"Auditorium 10","end_time":"04:33 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":8,"start_time":"2:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364092&CinemarkMovieId=97171&Showtime=2024-07-30T14:00:00&LinkedShowtimeId=364109"},{"auditorium_number":"Auditorium 4","end_time":"04:50 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":29,"start_time":"2:50 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368936&CinemarkMovieId=96523&Showtime=2024-07-30T14:50:00"},{"auditorium_number":"Auditorium 9","end_time":"05:03 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":72,"start_time":"2:30 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368002&CinemarkMovieId=97171&Showtime=2024-07-30T14:30:00"},{"auditorium_number":"Auditorium 3","end_time":"05:05 PM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":14,"start_time":"3:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368930&CinemarkMovieId=96521&Showtime=2024-07-30T15:00:00"},{"auditorium_number":"Auditorium 2","end_time":"05:40 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":23,"start_time":"3:40 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368925&CinemarkMovieId=96523&Showtime=2024-07-30T15:40:00"},{"auditorium_number":"Auditorium 1","end_time":"05:56 PM","movie_name":"Longlegs","run_time":[1,41],"seats_unavailable":15,"start_time":"3:50 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368923&CinemarkMovieId=96524&Showtime=2024-07-30T15:50:00"},{"auditorium_number":"Auditorium 5","end_time":"06:01 PM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":7,"start_time":"4:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368941&CinemarkMovieId=96520&Showtime=2024-07-30T16:00:00"},{"auditorium_number":"Auditorium 11","end_time":"06:18 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":44,"start_time":"3:45 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364096&CinemarkMovieId=97171&Showtime=2024-07-30T15:45:00&LinkedShowtimeId=364105"},{"auditorium_number":"Auditorium 6","end_time":"06:37 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":21,"start_time":"4:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368946&CinemarkMovieId=96525&Showtime=2024-07-30T16:10:00"},{"auditorium_number":"Auditorium 8","end_time":"06:38 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":85,"start_time":"4:05 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368009&CinemarkMovieId=97171&Showtime=2024-07-30T16:05:00"},{"auditorium_number":"Auditorium XD","end_time":"07:03 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":160,"start_time":"4:30 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364101&CinemarkMovieId=97171&Showtime=2024-07-30T16:30:00"},{"auditorium_number":"Auditorium 7","end_time":"07:28 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":34,"start_time":"4:55 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368000&CinemarkMovieId=97171&Showtime=2024-07-30T16:55:00"},{"auditorium_number":"Auditorium 3","end_time":"07:45 PM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":24,"start_time":"5:40 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368931&CinemarkMovieId=96521&Showtime=2024-07-30T17:40:00"},{"auditorium_number":"Auditorium 10","end_time":"07:48 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":93,"start_time":"5:15 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364093&CinemarkMovieId=97171&Showtime=2024-07-30T17:15:00&LinkedShowtimeId=364110"},{"auditorium_number":"Auditorium 4","end_time":"07:57 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":52,"start_time":"5:30 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368937&CinemarkMovieId=96525&Showtime=2024-07-30T17:30:00"},{"auditorium_number":"Auditorium 2","end_time":"08:15 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":88,"start_time":"6:15 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368926&CinemarkMovieId=96523&Showtime=2024-07-30T18:15:00"},{"auditorium_number":"Auditorium 9","end_time":"08:18 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":121,"start_time":"5:45 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368003&CinemarkMovieId=97171&Showtime=2024-07-30T17:45:00"},{"auditorium_number":"Auditorium 1","end_time":"08:31 PM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":59,"start_time":"6:30 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368919&CinemarkMovieId=96520&Showtime=2024-07-30T18:30:00"},{"auditorium_number":"Auditorium 5","end_time":"09:08 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":102,"start_time":"6:35 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=369053&CinemarkMovieId=97171&Showtime=2024-07-30T18:35:00"},{"auditorium_number":"Auditorium 11","end_time":"09:33 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":130,"start_time":"7:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364097&CinemarkMovieId=97171&Showtime=2024-07-30T19:00:00&LinkedShowtimeId=364106"},{"auditorium_number":"Auditorium 6","end_time":"09:37 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":86,"start_time":"7:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368947&CinemarkMovieId=96525&Showtime=2024-07-30T19:10:00"},{"auditorium_number":"Auditorium 8","end_time":"09:53 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":110,"start_time":"7:20 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368008&CinemarkMovieId=97171&Showtime=2024-07-30T19:20:00"},{"auditorium_number":"Auditorium XD","end_time":"10:18 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":248,"start_time":"7:45 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364102&CinemarkMovieId=97171&Showtime=2024-07-30T19:45:00"},{"auditorium_number":"Auditorium 3","end_time":"10:25 PM","movie_name":"A Quiet Place: Day One","run_time":[1,40],"seats_unavailable":56,"start_time":"8:20 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368932&CinemarkMovieId=96521&Showtime=2024-07-30T20:20:00"},{"auditorium_number":"Auditorium 7","end_time":"10:43 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":98,"start_time":"8:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368006&CinemarkMovieId=97171&Showtime=2024-07-30T20:10:00"},{"auditorium_number":"Auditorium 2","end_time":"10:50 PM","movie_name":"Despicable Me 4","run_time":[1,35],"seats_unavailable":90,"start_time":"8:50 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368927&CinemarkMovieId=96523&Showtime=2024-07-30T20:50:00"},{"auditorium_number":"Auditorium 10","end_time":"11:03 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":115,"start_time":"8:30 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=364094&CinemarkMovieId=97171&Showtime=2024-07-30T20:30:00&LinkedShowtimeId=364111"},{"auditorium_number":"Auditorium 4","end_time":"11:07 PM","movie_name":"Twisters","run_time":[2,2],"seats_unavailable":78,"start_time":"8:40 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368938&CinemarkMovieId=96525&Showtime=2024-07-30T20:40:00"},{"auditorium_number":"Auditorium 1","end_time":"11:11 PM","movie_name":"Inside Out 2","run_time":[1,36],"seats_unavailable":26,"start_time":"9:10 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368920&CinemarkMovieId=96520&Showtime=2024-07-30T21:10:00"},{"auditorium_number":"Auditorium 9","end_time":"11:33 PM","movie_name":"Deadpool & Wolverine","run_time":[2,8],"seats_unavailable":121,"start_time":"9:00 PM","url":"/TicketSeatMap/?TheaterId=1085&ShowtimeId=368004&CinemarkMovieId=97171&Showtime=2024-07-30T21:00:00"}]
daily_scheduler:BackgroundScheduler = BackgroundScheduler()
fresh_data_scheduler:BackgroundScheduler  = BackgroundScheduler()
daily_scheduler_initialized = False

def daily_task():
    global all_movie_run_times
    global movie_showings
    global fresh_data_scheduler
    if fresh_data_scheduler.running:
        fresh_data_scheduler.remove_all_jobs()
    else:
        fresh_data_scheduler.start()

    all_movie_run_times =  asyncio.run(get_all_movies_with_runtime())
    movie_showings = asyncio.run(get_all_movie_showings())
    for showing in movie_showings:
        try:
            formatted_time = parse_and_format_time(showing[4])
            hour, minute = map(int, formatted_time.split(':'))
            app.logger.info(formatted_time)
            app.logger.info(hour)
            app.logger.info(minute)
            app.logger.info(showing[2])
            fresh_data_scheduler.add_job(func = update_movie, trigger='cron',args=(showing[2],), hour=hour, minute=minute,timezone='America/Los_Angeles')
        except:
            app.logger.info("an error occurred parsing time for movie update scheduler")



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
        str_name =str(element)
        str_name = str_name.replace("&amp;","&")
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
async def get_all_movies_with_runtime():
    response = requests.get(main_movie_url+"/movies/now-playing")
    movie_runtime_dict = defaultdict(default_arr)
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return movie_runtime_dict
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    anchor_tags = soup.find_all('a', class_="movie-poster")
    hrefs = [a.get('href') for a in anchor_tags if a.get('href')]
    # limit =4
    for movie_link in hrefs:
        try:
            response = requests.get(main_movie_url+str(movie_link))
            if response.status_code == 200:
                html_content = response.text
                # Parse the HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                movie_name_element = soup.find(class_='movie-detail-title')
                movie_name= str(movie_name_element.text.strip())
                app.logger.info(movie_name)
                # Extract elements with a specific class
                movie_runtime_element = soup.find_all(class_='movie-detail-runtime')
                hours_minutes = get_movie_hours_minutes(movie_runtime_element)
                movie_runtime_dict[movie_name]=hours_minutes
                await asyncio.sleep(3)
            else:
                app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        except:
            app.logger.info("error getting response, movie link: "+ str(movie_link))
        finally:
            response.close()
            gc.collect()

        # if limit<=0:
        #     break
        # limit-=1
    return movie_runtime_dict
        
#start_time:str, duration:list
def calculate_end_time(start_time_str:str, runtime:list):
    # start_time_str = "11:15 am"
    # runtime = [2, 30]  # 2 hours and 30 minutes

    app.logger.info(start_time_str)
    app.logger.info(runtime)
    # Step 1: Parse the start time string into a datetime object
    start_time = datetime.strptime(start_time_str, "%I:%M %p")

    # Step 2: Create a timedelta object for the runtime
    runtime_delta = timedelta(hours=runtime[0], minutes=runtime[1]+25)

    # Step 3: Calculate the end time by adding the runtime to the start time
    end_time = start_time + runtime_delta

    # Step 4: Format the end time as a string if needed
    end_time_str = end_time.strftime("%I:%M %p")

    app.logger.info("Start Time:"+ start_time_str)
    app.logger.info(f"Runtime: {runtime[0]} hours and {runtime[1]} minutes")
    app.logger.info("End Time:"+ end_time_str)
    return end_time_str


def get_auditorium_details(path:str):
    global all_movie_run_times
    movie_name=""
    auditorium_number="query failed"
    start_time = "01:00"
    run_time =[0,0]
    end_time = '01:00 AM'
    seats_unavailable = 0
    try:
        response = requests.get(main_movie_url+path)
        if response.status_code!=200:
            app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return ['','query failed',path,0,"01:00 AM",[0,0],'01:00 AM']
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            movie_name = str(soup.find(class_='seats-tickets-title').text.strip())
        except:
            app.logger.info("getting movie name failed")
        try:
            auditorium_number= str(soup.find(class_='auditoriumNumber').text.strip())
        except:
            app.logger.info("getting auditorium number failed")
        try:
            start_time = str(soup.find(class_='seats-tickets-time').text.strip())
            app.logger.info(movie_name)
            app.logger.info(all_movie_run_times[movie_name])
            run_time = all_movie_run_times[movie_name]
            end_time = calculate_end_time(start_time,run_time)
        except:
            app.logger.info("getting times failed")
        try:
            seat_map = soup.find(class_='seatMap')
            seats_unavailable = len(seat_map.find_all(class_='seatUnavailable seatBlock'))
        except:
            app.logger.info("getting seats failed")
        app.logger.info(start_time)
        app.logger.info(movie_name)
        app.logger.info(auditorium_number)
        app.logger.info(seats_unavailable)
    except:
        app.logger.info("trouble with path: "+ path)
    finally:
            response.close()
            gc.collect()
    return [movie_name,auditorium_number,path,seats_unavailable,start_time,run_time,end_time]
    

def update_movie(path):
    global movie_showings
    latest_movie_showing_details = get_auditorium_details(path)
    for i in range(len(movie_showings)):
        if movie_showings[i][2]==path:
            app.logger.info(movie_showings[i])
            app.logger.info('updating latest')
            app.logger.info(latest_movie_showing_details)
            for j in range(len(movie_showings[i])):
                movie_showings[i][j]=latest_movie_showing_details[j]
    return latest_movie_showing_details

def convert_time_to_datetime(time_str):
    return datetime.strptime(time_str, "%I:%M %p")
def parse_and_format_time(input_time, output_format="%H:%M"):
    # Parse the input time string
    dt = datetime.strptime(input_time, "%I:%M %p")
    dt+= timedelta(minutes=15)
    # Format the datetime object to the desired format
    formatted_time = dt.strftime(output_format)
    
    return formatted_time

async def get_all_movie_showings():
    global all_movie_run_times
    response = requests.get(target_theatre_url)
    movies = []
    if response.status_code!=200:
        app.logger.info(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return movies
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    anchor_tags = soup.find_all(class_='showtime-link')
    hrefs = [a.get('href') for a in anchor_tags if a.get('href')]
    # limit = 2
    for showtime_path in hrefs:
        path= str(showtime_path)
        auditorium= get_auditorium_details(path)
        movies.append(auditorium)
        await asyncio.sleep(10)
        # if limit<=0:
        #     break
        # limit-=1
    sorted_times_list = sorted(movies, key=lambda x: convert_time_to_datetime(x[6]))
    app.logger.info(sorted_times_list)
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
        daily_task()
        daily_scheduler.add_job(daily_task, CronTrigger(hour=3, minute=0,timezone='America/Los_Angeles'))
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

@app.route('/api/get_html', methods=['GET'])
def show_all_movies():
    global movie_showings
    return render_template('index.html', items=movie_showings)

# Run the app
if __name__ == '__main__':
    try:
        daily_task()
        app.run(port=8000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        daily_scheduler.shutdown()
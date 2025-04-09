from flask import Flask
import logging
import psycopg2
import os


# Define your connection parameters
conn_params = {
    'dbname': 'd2lrupfmegs85s',
    'user': 'u2kifcd3qbui9r',
    'password': 'p6cd021c042a7ae698de46521aaad30ed6722250de44be5f9d1c01527580e99d8',
    'host': 'ccba8a0vn4fb2p.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',  # or your database server IP
    'port': '5432'  # default PostgreSQL port
}
connection =None
try:
    connection = psycopg2.connect(**conn_params)
    cursor = connection.cursor()
    print("Connection successful")
except Exception as e:
    print(f"Error connecting to database: {e}")

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

player_data = {
    'player_uuid': '1234-5678-90ab-cdef12345678',
    'user_name': 'PlayerName',
    'email': 'player@example.com',
    'leaderboard_rank': 1,
    'friendship_uuid': '1234-5678-90ab-cdef12345678'
}
insert_query = """
INSERT INTO player (player_uuid, user_name, email, leaderboard_rank, friendship_uuid) 
VALUES (%s, %s, %s, %s, %s);
"""
@app.route('/create/')
def create():
    cursor = connection.cursor()
    print("Connection successful")

    # Execute the insert statement
    cursor.execute(insert_query, (
        player_data['player_uuid'],
        player_data['user_name'],
        player_data['email'],
        player_data['leaderboard_rank'],
        player_data['friendship_uuid']
    ))
    
    # Commit the transaction
    connection.commit()
    print("Player inserted successfully")
    return "success"
# Define a route for the default URL, which loads the homepage
@app.route('/<username>')
def home(username):
    global connection
    query = "SELECT * FROM player;"

    try:
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all results
        for row in results:
            print(row)  # Print each row
    except Exception as e:
        print(f"Error executing query: {e}")
    return "results"
    #return "Welcome to the Flask API!"
# Run the app
if __name__ == '__main__':
    try:
        #daily_task()

        app.run(port=8000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        daily_scheduler.shutdown()
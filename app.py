from flask import Flask, jsonify, request, redirect, render_template, url_for, send_file
import qrcode
import io
import logging
import psycopg2
import uuid
from collections import defaultdict
from google_sheets import write_to_google_sheet
import time
import datetime

unique_ID_sign_up = {"status":"scanning","scan_count":0,"completed_count":0}
unique_ID_sign_in = {"status":"scanning","scan_count":0,"completed_count":0}
current_QR_UUID_sign_up = "initial_value"
current_QR_UUID_sign_in = "initial_value"
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
scan_cap = 10


def generate_sign_up():
    global current_QR_UUID_sign_up
    sessionID = str(uuid.uuid4())
    unique_ID_sign_up[sessionID]={"status":"scanning","scan_count":0,"completed_count":0}
    data = {
        'message': sessionID,
        'status': 'success'
    }
    current_QR_UUID_sign_up = sessionID
    print(current_QR_UUID_sign_up)
    return data
def generate_sign_in():
    global current_QR_UUID_sign_in
    sessionID = str(uuid.uuid4())
    unique_ID_sign_in[sessionID]={"status":"scanning","scan_count":0,"completed_count":0}
    data = {
        'message': sessionID,
        'status': 'success'
    }
    current_QR_UUID_sign_in = sessionID
    print(current_QR_UUID_sign_in)
    return data

@app.route('/generateUnique/')
def updateUniqueID():
    return jsonify(generate_sign_up())


@app.route('/useSession/sign_up/<sessionID>', methods=['GET', 'POST'])
def use_session_sign_up(sessionID):
    # Check if the session ID exists in the dictionary and is in "waiting" state
    if(unique_ID_sign_up.get(sessionID)==None):
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)
    if sessionID in unique_ID_sign_up and unique_ID_sign_up[sessionID]["completed_count"] >= scan_cap:
        del unique_ID_sign_up[sessionID]
    if sessionID in unique_ID_sign_up and unique_ID_sign_up[sessionID]["completed_count"] < scan_cap:
        if request.method == 'POST':
            # Get the name from the form submission (POST request)
            # Get the name from the form submission (POST request)
            unique_ID_sign_up[sessionID]["completed_count"]+=1
            first_name = request.form.get('first_name')  # Name is submitted via the form
            last_name = request.form.get('last_name')
            student_type = request.form.get('student_type')
            year = request.form.get('year')
            email = request.form.get('email')
            current_timestamp = time.time()
            datetime_object = datetime.datetime.fromtimestamp(current_timestamp)
            write_to_google_sheet(["sign-up",str(first_name),str(last_name),str(email),str(student_type),str(year), str(datetime_object)])
            # Redirect to the success page
            return redirect(url_for('success', sessionID=sessionID, name=first_name))
            #return render_template('signUp.html', message=message, status=status)

        # If it's a GET request, show the form
        return render_template('signUp.html', sessionID=sessionID, message=None, status=None)

    else:
        # If session ID is invalid or already used
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)
@app.route('/useSession/sign_in/<sessionID>', methods=['GET', 'POST'])
def use_session_sign_in(sessionID):
    # Check if the session ID exists in the dictionary and is in "waiting" state
    if(unique_ID_sign_in.get(sessionID)==None):
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signIn.html', message=message, status=status)
    if sessionID in unique_ID_sign_in and unique_ID_sign_in[sessionID]["completed_count"] >= scan_cap:
        del unique_ID_sign_in[sessionID]
    if sessionID in unique_ID_sign_in and unique_ID_sign_in[sessionID]["completed_count"] < scan_cap:
        if request.method == 'POST':
            # Get the name from the form submission (POST request)
            # Get the name from the form submission (POST request)
            unique_ID_sign_in[sessionID]["completed_count"]+=1
            first_name = request.form.get('first_name')  # Name is submitted via the form
            last_name = request.form.get('last_name')
            current_timestamp = time.time()
            datetime_object = datetime.datetime.fromtimestamp(current_timestamp)
            write_to_google_sheet(["sign-in",str(first_name),str(last_name),str(datetime_object)])
            # Redirect to the success page
            return redirect(url_for('success', sessionID=sessionID, name=first_name))
            #return render_template('signUp.html', message=message, status=status)

        # If it's a GET request, show the form
        return render_template('signIn.html', sessionID=sessionID, message=None, status=None)

    else:
        # If session ID is invalid or already used
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signIp.html', message=message, status=status)

# Success screen route
@app.route('/success')
def success():
    sessionID = request.args.get('sessionID')
    name = request.args.get('name')

    # You can display the session ID and name on the success screen
    return render_template('success.html', sessionID=sessionID, name=name)
    

@app.route('/sign_up')
def signUp():
    return render_template('qrCodeSignUp.html')

@app.route('/sign_in')
def signIn():
    return render_template('qrCodeSignIn.html')

# Endpoint to generate the current QR code
@app.route('/generate_qr_sign_up', methods=['GET'])
def generate_qr_code_sign_up():
    global current_QR_UUID_sign_up
    
    # Generate QR code based on the current data
    img = qrcode.make(request.host_url+"scan/sign_up/"+current_QR_UUID_sign_up)
    
    # Save the image in memory and return it as a response
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

# Endpoint to generate the current QR code
@app.route('/generate_qr_sign_in', methods=['GET'])
def generate_qr_code_sign_in():
    global current_QR_UUID_sign_in
    
    # Generate QR code based on the current data
    img = qrcode.make(request.host_url+"scan/sign_in/"+current_QR_UUID_sign_in)
    
    # Save the image in memory and return it as a response
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')
# Endpoint that simulates the user scanning the QR code and validating the URL
@app.route('/scan/sign_in/<sessionID>', methods=['GET'])
def scan_sign_in(sessionID):
    global unique_ID_sign_in
    if(unique_ID_sign_in.get(sessionID)==None):
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signIn.html', message=message, status=status)
    if(unique_ID_sign_in[sessionID]["scan_count"] > scan_cap):
        # Once the session ID is used, delete it from the dictionary
        #del unique_ID_sign_in[sessionID]
        generate_sign_up()
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signIn.html', message=message, status=status)
    # Check if the sessionID exists and is still in the "waiting" state
    if sessionID in unique_ID_sign_in and unique_ID_sign_in[sessionID]["scan_count"] < scan_cap:
        unique_ID_sign_in[sessionID]["scan_count"]+=1
        if(unique_ID_sign_in[sessionID]["scan_count"] == scan_cap):
            #del unique_ID_sign_in[sessionID]
            unique_ID_sign_in[sessionID]["status"]="submitting"
            generate_sign_up()
        # If it's a GET request, show the form to enter the name
        return render_template('signIn.html', sessionID=sessionID, message=None, status=None)

    else:
        # If session ID is invalid or already used
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)
# Endpoint that simulates the user scanning the QR code and validating the URL
@app.route('/scan/sign_up/<sessionID>', methods=['GET'])
def scan_sign_up(sessionID):
    global unique_ID_sign_up
    if(unique_ID_sign_up.get(sessionID)==None):
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)
    if(unique_ID_sign_up[sessionID]["scan_count"] > scan_cap):
        # Once the session ID is used, delete it from the dictionary
        #del unique_ID_sign_up[sessionID]
        generate_sign_up()
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)
    # Check if the sessionID exists and is still in the "waiting" state
    if sessionID in unique_ID_sign_up and unique_ID_sign_up[sessionID]["scan_count"] < scan_cap:
        unique_ID_sign_up[sessionID]["scan_count"]+=1
        if(unique_ID_sign_up[sessionID]["scan_count"] == scan_cap):
            #del unique_ID_sign_up[sessionID]
            unique_ID_sign_up[sessionID]["status"]="submitting"
            generate_sign_up()
        # If it's a GET request, show the form to enter the name
        return render_template('signUp.html', sessionID=sessionID, message=None, status=None)

    else:
        # If session ID is invalid or already used
        message = "Session ID is invalid or already used."
        status = "error"
        return render_template('signUp.html', message=message, status=status)

generate_sign_up()
generate_sign_in()
# Run the app
if __name__ == '__main__':
    try:
        #daily_task()
        app.run( host='127.0.0.1', port=8000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        daily_scheduler.shutdown()
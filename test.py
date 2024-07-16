from datetime import datetime, timedelta

def calculate_end_time(start_time_str:str, runtime:list):
    # start_time_str = "11:15 am"
    # runtime = [2, 30]  # 2 hours and 30 minutes

    print(start_time_str)
    print(runtime)
    # Step 1: Parse the start time string into a datetime object
    start_time = datetime.strptime(start_time_str, "%I:%M %p")

    # Step 2: Create a timedelta object for the runtime
    runtime_delta = timedelta(hours=runtime[0], minutes=runtime[1])

    # Step 3: Calculate the end time by adding the runtime to the start time
    end_time = start_time + runtime_delta

    # Step 4: Format the end time as a string if needed
    end_time_str = end_time.strftime("%I:%M %p")

    print(f"Start Time: {start_time_str}")
    print(f"Runtime: {runtime[0]} hours and {runtime[1]} minutes")
    print("End Time:"+ end_time_str)
    return end_time_str

s1= "3:10 PM"
t1 = [1,30]
result = calculate_end_time(s1,t1)
print(result)
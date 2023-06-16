from flask import Flask, render_template, copy_current_request_context
from threading import Thread
import csv
import time
import random
#import RPi.GPIO as GPIO

def write_csv(filename, time, value):
    with open(filename+'.csv', 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerow([time, value])

def read_csv_file(file_path):
    columns = []  # List to store the columns

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        header = next(csv_reader)  # Read the header row
        
        # Initialize empty lists for each column
        for _ in range(len(header)):
            columns.append([])

        # Iterate over each row and append values to respective columns
        for row in csv_reader:
            for i, value in enumerate(row):
                columns[i].append(float(value))

    return columns

def format_datetime(x):
    format_dt = '%Y-%m-%d %H:%M:%S'
    return time.strftime(format_dt, time.localtime(x))

def process_data():
    # Usage example
    file_path = 'noise_detection.csv'
    columns = read_csv_file(file_path)

    # Accessing columns by index
    column_1 = columns[0]
    column_2 = columns[1]

    # Data preprocessing

    formated_column_1 = [format_datetime(x) for x in column_1]
    return formated_column_1, column_2

app = Flask(__name__)

@app.route('/')
def index():
    thread = Thread(target=take_measurements)
    thread.start()
    return render_template('index.html')

@app.route('/logs')
def show_logs():
    logs = generate_logs()
    return render_template('logs.html', logs=logs)

@app.route('/noise')
def noise():
    column_1, column_2 = process_data()
    if len(column_1) >= 30:
        last_30_time = column_1[-30:]
        last_30_values = column_2[-30:]
        data_dict = {'datetime': last_30_time, 'value': last_30_values}
    else:
        data_dict = {'datetime': column_1, 'value': column_2}
    return render_template('plot_noise.html', data=data_dict)

def generate_logs():
    column_1, column_2 = process_data()

    seq = find_consecutive_ones_indices(column_2)

    log_list = []
    for start_noise, end_noise in seq:
        len_noise = end_noise + 1 - start_noise
        start_time = column_1[start_noise]
        end_time = column_1[end_noise]
        log = f'Un sonido de {len_noise} segundos fue detectado entre {start_time} y {end_time}'
        log_list.append(log)
    return log_list

def find_consecutive_ones_indices(binary_list):
    sequences = []
    start_index = -1
    for i, num in enumerate(binary_list):
        if num == 1 and start_index == -1:
            start_index = i
        elif num == 0 and start_index != -1:
            end_index = i - 1
            if end_index - start_index >= 2:
                sequences.append((start_index, end_index))
            start_index = -1

    # Check if there are consecutive ones at the end of the list
    if start_index != -1 and len(binary_list) - start_index >= 3:
        sequences.append((start_index, len(binary_list) - 1))

    return sequences

def take_measurements():
    filename = 'C:/Users/elisa/Documents/2023-1/Lab_TICs/Proyecto/noise_detection'
    start_time_measurements = time.time()
    while True:
        current_time = time.time()
        elapsed_time_measurements = current_time - start_time_measurements
        if abs(elapsed_time_measurements - 15) < 0.001:
            # Deja de tomar mediciones
            break
        value = bool(random.randint(0, 1))

        if value:
            write_csv(filename, current_time, 1)
        else:
            write_csv(filename, current_time, 0)


# def take_measurements():
#     #GPIO SETUP
#     # Sound sensor
#     do_channel = 17 # GPIO
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(do_channel, GPIO.IN)

#     # LED
#     led_pin = 21 #Escribir el pin del LED
#     GPIO.setup(led_pin, GPIO.OUT)
#     GPIO.output(led_pin, False)

#     filename = 'noise_detection'
#     registered_values = []
#     start_time = time.time()
#     start_time_measurements = time.time()
#     while True:
#         registered_values.append(GPIO.input(do_channel))
#         current_time = time.time()
#         elapsed_time = current_time - start_time

#         elapsed_time_measurements = current_time - start_time_measurements
#         if abs(elapsed_time_measurements - 60) < 0.001:
#             # Deja de tomar mediciones
#             break

#         if abs(elapsed_time - 1) < 0.001:  # Pasa 1 segundo   
#             if any(registered_values):
#                 write_csv(filename, current_time, 1)
#                 print('Encontre ruido')
#                 GPIO.output(led_pin, True)
#             else:
#                 write_csv(filename, current_time, 0)
#                 print('No encontre ruido')
#                 GPIO.output(led_pin, False)
            
#             registered_values = []
#             start_time = time.time()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

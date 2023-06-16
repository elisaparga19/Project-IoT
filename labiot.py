import RPi.GPIO as GPIO
import time
import csv
import os

def write_csv(filename, time, value):
    with open(filename+'.csv', 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerow([time, value])

#GPIO SETUP
# Sound sensor
do_channel = 17 # GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(do_channel, GPIO.IN)

# LED
led_pin = 21 #Escribir el pin del LED
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, False)

filename = 'noise_detection'
# global_values = []
registered_values = []
start_time = time.time()
while True:
    registered_values.append(GPIO.input(do_channel))
    current_time = time.time()
    elapsed_time = current_time - start_time

    if abs(elapsed_time - 1) < 0.001:  # Pasa 1 segundo   
        if any(registered_values):
            write_csv(filename, current_time, 1)
            print('Encontre ruido')
            GPIO.output(led_pin, True)
        else:
            write_csv(filename, current_time, 0)
            print('No encontre ruido')
            GPIO.output(led_pin, False)
        
        registered_values = []
        start_time = time.time()

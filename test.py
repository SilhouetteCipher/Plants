#!/usr/bin/env python3

import argparse
from PIL import Image
from inky.auto import auto
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont




# Define MQTT parameters
MQTT_BROKER = "10.224.1.7"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPICS_SUBSCRIBED = 0
MAX_TOPICS = 5
mqtt_data = []

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    # Subscribing to a wildcard topic
    client.subscribe("plants/moisture/#")

def on_message(client, userdata, msg):
    global MQTT_TOPICS_SUBSCRIBED
    if MQTT_TOPICS_SUBSCRIBED < MAX_TOPICS:
        print(f"Received message on topic {msg.topic} with payload {msg.payload}")
        MQTT_TOPICS_SUBSCRIBED += 1
        mqtt_data.append({"topic": msg.topic, "value": float(msg.payload)})

# Setup the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

# Start the loop
client.loop_start()





# Set up the inky wHAT display and border colour

inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)

# Grab the image argument from the command line



# Open our image file that was passed in from the command line

img = Image.open("/home/davvyk/Plants/test.jpg")

# Get the width and height of the image

w, h = img.size

# Calculate the new height and width of the image

h_new = 300
w_new = int((float(w) / h) * h_new)
w_cropped = 400

# Resize the image with high-quality resampling

img = img.resize((w_new, h_new), resample=Image.LANCZOS)

# Calculate coordinates to crop image to 400 pixels wide

x0 = (w_new - w_cropped) / 2
x1 = x0 + w_cropped
y0 = 0
y1 = h_new

# Crop image

img = img.crop((x0, y0, x1, y1))

# Convert the image to use a white / black / red colour palette

pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

img = img.convert("RGB").quantize(palette=pal_img)

# Bar Charting

# Setting the values as per your constraints
bar_width = 41
spacing = 34
max_bar_height = 155
starting_x = 36

draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

for index, data in enumerate(mqtt_data):
    x = starting_x + index * (bar_width + spacing)
    y = inky_display.height - 22 - (data["value"] / 100) * max_bar_height  # Adjusting the start Y position
    draw.rectangle((x, y, x + bar_width, inky_display.height - 22), fill=inky_display.YELLOW)  # Adjusted the base Y position
    label_width, label_height = draw.textsize(data["topic"], font)
    label_x = x + (bar_width - label_width) / 2
    label_y = inky_display.height - 22 + 5  # 5 pixels below the base of the bar
    draw.text((label_x, label_y), data["topic"], font=font, fill=inky_display.YELLOW)



# Display the final image on Inky wHAT

inky_display.set_image(img)
inky_display.show()

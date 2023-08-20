

#!/usr/bin/env python3

import argparse
from PIL import Image
from inky.auto import auto
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont

# create a function that takes my mqtt payload and then gives me a variable i can edit for each one for min and max values

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



def draw_rounded_rect(draw, xy, corner_radius, fill=None):
    """Draw a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle(
        [(x1, y1 + corner_radius), (x2, y2 - corner_radius)],
        fill=fill
    )
    draw.rectangle(
        [(x1 + corner_radius, y1), (x2 - corner_radius, y2)],
        fill=fill
    )
    draw.pieslice(
        [x1, y1, x1 + 2*corner_radius, y1 + 2*corner_radius],
        180, 270, fill=fill
    )
    draw.pieslice(
        [x2 - 2*corner_radius, y1, x2, y1 + 2*corner_radius],
        270, 360, fill=fill
    )
    draw.pieslice(
        [x1, y2 - 2*corner_radius, x1 + 2*corner_radius, y2],
        90, 180, fill=fill
    )
    draw.pieslice(
        [x2 - 2*corner_radius, y2 - 2*corner_radius, x2, y2],
        0, 90, fill=fill
    )

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

img = Image.open("/home/davvyk/Plants/Plants.jpg")

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

# Convert the image to use a white / black / yellow colour palette
pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 255, 0) + (0, 0, 0) * 252)

img = img.convert("RGB").quantize(palette=pal_img)


# Bar Charting

bar_width = 40.6
spacing = 33.7
max_bar_height = 155  # Maximum height of the bar
max_data_value = 3000  # Maximum value from the data
border_thickness = 10
starting_x = 35.6

font_path = "/home/davvyk/Plants/distinct.ttf"
font_size = 11  # You can adjust this to your preference
font = ImageFont.truetype(font_path, font_size)
draw = ImageDraw.Draw(img)




for index, data in enumerate(mqtt_data):
    x = starting_x + index * (bar_width + spacing)
    proportion = data["value"] / max_data_value
    calculated_bar_height = proportion * max_bar_height
    y = inky_display.height - 22 - calculated_bar_height

    # Draw the actual bar with rounded corners
    draw_rounded_rect(draw, (x, y, x + bar_width, inky_display.height - 22), corner_radius=10, fill=inky_display.YELLOW)
    
    # ... rest of your code ...

    
    # Draw white border
   #  draw.rectangle((x - border_thickness, y - border_thickness, x + bar_width + border_thickness, inky_display.height - 22 + border_thickness), fill=inky_display.WHITE)
    
    # Draw the actual bar inside the white border
    #draw.rectangle((x, y, x + bar_width, inky_display.height - 22), fill=inky_display.YELLOW)
    
    # Display topic labels
    short_topic = ' '.join(data["topic"].split("/")[-1])
    # Display topic labels
    descender = font.getmetrics()[1]
    label_height, label_width = draw.textsize(short_topic, font).strip()
    label_x = x + bar_width + 1
    label_y = 130

    draw.text((label_x, label_y), short_topic, font=font, fill=inky_display.BLACK, direction="ttb")

    padding = 5  # Adjust this value to increase/decrease the padding
    background_rect = (
        label_x - padding,
        label_y - padding,
        label_x + label_width + padding,
        label_y + label_height + padding
    )
    #draw.rectangle(background_rect, fill=inky_display.WHITE)


   


# Display the final image on Inky wHAT

inky_display.set_image(img)
inky_display.show()
img.save("output.png")

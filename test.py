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
    draw.rectangle([(x1, y1 + corner_radius), (x2, y2 - corner_radius)], fill=fill)
    draw.rectangle([(x1 + corner_radius, y1), (x2 - corner_radius, y2)], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*corner_radius, y1 + 2*corner_radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*corner_radius, y1, x2, y1 + 2*corner_radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*corner_radius, x1 + 2*corner_radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*corner_radius, y2 - 2*corner_radius, x2, y2], 0, 90, fill=fill)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
client.loop_start()

inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)
img = Image.open("/home/davvyk/Plants/Plants.jpg")
w, h = img.size
h_new = 300
w_new = int((float(w) / h) * h_new)
w_cropped = 400
img = img.resize((w_new, h_new), resample=Image.LANCZOS)
x0 = (w_new - w_cropped) / 2
x1 = x0 + w_cropped
y0 = 0
y1 = h_new
img = img.crop((x0, y0, x1, y1))

pal_img = Image.new("P", (1, 1))
pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 255, 0) + (0, 0, 0) * 252)
img = img.convert("RGB").quantize(palette=pal_img)

bar_width = 40.6
spacing = 33.7
max_bar_height = 155
max_data_value = 3000
border_thickness = 10
starting_x = 35.6

font_path = "/home/davvyk/Plants/distinct.ttf"
font_size = 11
font = ImageFont.truetype(font_path, font_size)

canvas = Image.new('RGBA', img.size, (255, 255, 255, 0))
canvas_draw = ImageDraw.Draw(canvas)

for index, data in enumerate(mqtt_data):
    x = starting_x + index * (bar_width + spacing)
    proportion = data["value"] / max_data_value
    calculated_bar_height = proportion * max_bar_height
    y = inky_display.height - 22 - calculated_bar_height
    draw_rounded_rect(canvas_draw, (x, y, x + bar_width, inky_display.height - 22), corner_radius=10, fill=inky_display.YELLOW)

    label = data["topic"].split("/")[-1]
    text_width, text_height = canvas_draw.textsize(label, font)
    text_img = Image.new('P', (text_width, text_height), color=inky_display.WHITE)
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((0, 0), label, font=font, fill=inky_display.BLACK)
    rotated_text_img = text_img.rotate(90, expand=True)
    text_x = x + (bar_width / 2) - (text_height / 2)
    text_y = inky_display.height - 22 - (calculated_bar_height / 2) - (text_width / 2)
    mask = rotated_text_img.convert("L")
    canvas.paste(rotated_text_img, (int(text_x), int(text_y)), mask)

canvas = canvas.convert("RGB").quantize(palette=pal_img)
img.paste(canvas, (0, 0), canvas)
inky_display.set_image(img)
inky_display.show()

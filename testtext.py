from inky import InkyWHAT
from PIL import Image

# Create an Inky wHAT display object
display = InkyWHAT("yellow")  # Replace "yellow" with "red" if you have the red variant

# Load the image using the Python Imaging Library (PIL)
img = Image.open("/home/davvyk/Plants/test.jpeg")

# Set the image on the display and show it
display.set_image(img)
display.show()

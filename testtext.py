from inky import InkyWHAT
from PIL import Image
from inky.auto import auto

# Create an Inky wHAT display object
display = InkyWHAT("yellow")  # Replace "yellow" with "red" if you have the red variant

# Load the image using the Python Imaging Library (PIL)
img = Image.open("/home/davvyk/Plants/test.jpg")

img_gray = img.convert('L')

# Set the image on the display and show it
display = auto()
display.set_image(img)
display.show()

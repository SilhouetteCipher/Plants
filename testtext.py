from inky import InkyWHAT
from PIL import Image
from inky.auto import auto

# Create an Inky wHAT display object
display = InkyWHAT("yellow")  # Replace "yellow" with "red" if you have the red variant

# Load the image using the Python Imaging Library (PIL)
img = Image.open("/home/davvyk/Plants/test.jpg")

# Convert image to RGB
img_rgb = img.convert("RGB")

# Define the palette colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 235, 59)  # An approximation; you might adjust this based on your design.

def closest_color(rgb):
    colors = [BLACK, WHITE, YELLOW]
    closest_colors = sorted(colors, key=lambda color: sum((a-b) ** 2 for a, b in zip(color, rgb)))
    return closest_colors[0]

# Create a new image with the palette colors
width, height = img_rgb.size
new_img = Image.new("RGB", (width, height))

for x in range(width):
    for y in range(height):
        pixel = img_rgb.getpixel((x, y))
        new_img.putpixel((x, y), closest_color(pixel))

# Save the processed image (optional)
new_img.save("processed_image.png")

# Use with Inky wHAT
from inky.auto import auto
display = auto()
display.set_image(new_img)
display.show()

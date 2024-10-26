import numpy as np
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

# Function to calculate the minimum distance from all colors and get the most matching color
def getColorName(R, G, B, csv):
    minimum = 10000
    cname = ""
    
    # Convert RGB values to int for safe arithmetic operations
    R, G, B = int(R), int(G), int(B)
    
    for i in range(len(csv)):
        # Convert the CSV values to int for proper comparison and avoid overflow
        r_val = int(csv.loc[i, "R"])
        g_val = int(csv.loc[i, "G"])
        b_val = int(csv.loc[i, "B"])
        
        # Calculate distance (abs ensures no negative values)
        d = abs(R - r_val) + abs(G - g_val) + abs(B - b_val)
        
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    
    return cname

# Function to get the RGB values from an image and detect the color name based on coordinates
def detect_color(image, csv, x, y):
    # Get RGB(A) values from the clicked point
    img = np.array(image)

    # Ensure the coordinates are within the image dimensions
    if 0 <= y < img.shape[0] and 0 <= x < img.shape[1]:
        pixel_values = img[y, x]
        if len(pixel_values) == 4:  # Image with RGBA values
            r, g, b, a = pixel_values
        else:  # Image with RGB values
            r, g, b = pixel_values
        # Get the closest color name from the CSV
        color_name = getColorName(r, g, b, csv)  # Use RGB values
        return color_name, r, g, b
    else:
        # Coordinates out of bounds, return None
        return None, None, None, None

# Load color data from CSV
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('colors.csv', names=index, header=None)

# Streamlit interface
st.title("Color Detection App with Drawable Canvas")

# Uploading an image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_array = np.array(image)

    # Slider for adjusting image display size
    image_scale = st.slider("Adjust Image Display Size:", min_value=100, max_value=1000, value=800)

    # Scale image for display
    scaled_width = int(image.width * (image_scale / 800))
    scaled_height = int(image.height * (image_scale / 800))
    resized_image = image.resize((scaled_width, scaled_height))

    # Add horizontal and vertical sliders for image panning only if the image is larger than the display area
    if scaled_width > 800:
        max_x_offset = scaled_width - 800
        x_offset = st.slider("Pan Horizontally:", min_value=0, max_value=max_x_offset, value=0)
    else:
        x_offset = 0

    if scaled_height > 600:
        max_y_offset = scaled_height - 600
        y_offset = st.slider("Pan Vertically:", min_value=0, max_value=max_y_offset, value=0)
    else:
        y_offset = 0

    # Crop the image based on the pan (sliders)
    cropped_image = resized_image.crop((x_offset, y_offset, x_offset + 800, y_offset + 600))

    # Display the cropped image on a drawable canvas
    st.write("Draw on the canvas to select colors.")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill color
        stroke_color="rgba(255, 0, 0, 1)",  # Red stroke color for visibility
        stroke_width=5,
        background_image=cropped_image,  # Use the cropped image
        update_streamlit=True,
        height=600,
        width=800,
        drawing_mode="point",
        point_display_radius=5,
        key="canvas",
    )

    # Variable to store last detected color information
    last_color_info = None

    if canvas_result.json_data is not None:
        # Extract coordinates of the clicked points
        if len(canvas_result.json_data["objects"]) > 0:
            for obj in canvas_result.json_data["objects"]:
                # Get coordinates of the clicked point
                x = int(obj["left"]) + x_offset
                y = int(obj["top"]) + y_offset

                # Check if the coordinates are within the bounds of the original image
                if 0 <= x < image.width and 0 <= y < image.height:
                    # Get color information at the clicked coordinates
                    color_name, r, g, b = detect_color(image, csv, x, y)
                    
                    if color_name is not None:
                        # Store the last detected color information
                        last_color_info = (color_name, r, g, b)

    # Display the last detected color information, if available
    if last_color_info:
        color_name, r, g, b = last_color_info
        st.write(f"Detected Color: {color_name}")
        st.write(f"RGB Values: R={r}, G={g}, B={b}")

        # Display a rectangle with the detected color
        st.markdown(f"<div style='background-color: rgb({r},{g},{b}); width:100px; height:100px;'></div>", unsafe_allow_html=True)

import os
import secrets
from PIL import Image
from flask import current_app

def save_picture(form_picture):
    # Generate a random hex to name the picture file
    random_hex = secrets.token_hex(8)
    # Get the file extension of the uploaded file
    _, f_ext = os.path.splitext(form_picture.filename)
    # Create the new filename
    picture_fn = random_hex + f_ext
    # Set the path where the file will be saved
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Save the picture
    i.save(picture_path)

    return picture_fn
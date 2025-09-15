import os
import shutil

UPLOAD_DIR = "uploads"

def save_upload_file(uploaded_file, destination_folder=UPLOAD_DIR):
    os.makedirs(destination_folder, exist_ok=True)
    file_location = os.path.join(destination_folder, uploaded_file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return file_location

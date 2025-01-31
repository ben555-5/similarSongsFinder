import os


VALID_EXTENSIONS = {".mp3", ".wav"}

# Receive file path from user
while True:
    file_path = input("Please enter the path to your audio file: ")

    # Check if the file exists
    if not os.path.exists(file_path):
        print("Error: File does not exist. Please enter a valid file path.")
        continue

    # Check if the file extension is valid
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in VALID_EXTENSIONS:
        print("Error: Invalid file format. Please enter a valid audio file (.mp3, .wav).")
        continue

    print("Valid file path received!")
    break

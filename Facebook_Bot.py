import requests
import os
from dotenv import load_dotenv
import schedule
import time
import json
import random

load_dotenv()
app_id = os.getenv("APP_ID")
page_id = os.getenv("PAGE_ID")
app_token = os.getenv("PAGE_TOKEN")
user_token = os.getenv("USER_TOKEN")
directory = os.getenv("GALLERY_DIRECTORY")
files = os.listdir(directory)
valid_files = []
posted_files = []

def RemoveInvalidFiles(CompleteFiles, PostedImages):
    for n in reversed(range(len(files))):
        root, extension = os.path.splitext(files[n])
        if extension in [".mp4", ".mp3", ".gif"] or CompleteFiles[n] in PostedImages:
            CompleteFiles.pop(n)
    return CompleteFiles

def PostImage():
    global valid_files, posted_files
    idFile = random.randint(0, len(valid_files) - 1)
    path = f"{directory}\\{valid_files[idFile]}"
    url = f"https://graph.facebook.com/v26.0/{page_id}/photos"
    params = {
        'access_token': app_token,
        "message": "(┬┬﹏┬┬)"
    }

    with open(path, "rb") as file:
        files = {
            "source": file
        }
        try:
            response = requests.post(url, params=params, files=files)
            result = response.json()
            print(result)
            if "id" in result:
                posted_files.append(valid_files[idFile])
                with open("Posted.json", "w") as file:
                    json.dump(posted_files, file)
                valid_files.pop(idFile)
            print("Files in queue: " + str(len(valid_files)))

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")


def Main(OriginalFiles):
    #Copy and paste for every time you want to post
    schedule.every().day.at("22:18").do(PostImage)
    schedule.every().day.at("22:20").do(PostImage)
    schedule.every().day.at("22:22").do(PostImage)


    global valid_files, posted_files
    with open("Posted.json", 'r') as jsonfile:
        posted_files = json.load(jsonfile)
    print("Original Files: " + str(len(OriginalFiles)))
    valid_files = RemoveInvalidFiles(OriginalFiles, posted_files)
    print("Valid Files: " + str(len(valid_files)))

    while True:
        schedule.run_pending()
        time.sleep(1)

Main(files)
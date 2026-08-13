import requests
import os
from dotenv import load_dotenv
import schedule
import time
import json
import random
import datetime

Directories = [
    "D:\\Pictures\\IControlReality", "D:\\Pictures\\FRUiTS 21-30", "D:\\Pictures\\Osaka Banpaku", 
    "D:\\Pictures\\PinappleKryptonite", "D:\\Pictures\\TemporaryHigh"
]

load_dotenv()
app_id = os.getenv("APP_ID")
page_id = os.getenv("PAGE_ID")
app_token = os.getenv("PAGE_TOKEN")
GFiles, GDirs, GPosted = [],[],[]

def DirectoryContent(directory, n):
    content = []
    files = os.listdir(directory)
    for file in files:
        content.append([file, n])
    return content

def OrganizeFiles(content, dirs):
    newDirectories = []
    for n in reversed(range(len(content))):
        root, extension = os.path.splitext(content[n][0])
        if extension == "":
            newDirectories.append(os.path.join(dirs[content[n][1]], root))
            content.pop(n)
    return [content, newDirectories]

def CleanFiles(files, PostedImages, BlackList):
    for n in reversed(range(len(files))):
        root, extension = os.path.splitext(files[n][0])
        if extension in [".mp4", ".mp3", ".gif"] or files[n][0] in PostedImages or files[n][0] in BlackList:
            files.pop(n)
    return files

def GetAllFiles(dirs):
    n = 0
    real_files = []
    for directory in dirs:
        content = DirectoryContent(directory, n)
        filesdirs = OrganizeFiles(content, dirs)
        for file in filesdirs[0]:
            real_files.append(file)
        for newdir in filesdirs[1]:
            dirs.append(newdir)
        n += 1
    return[real_files, dirs]

def PostImage():
    global GFiles, GDirs, GPosted
    with open("captions.json", 'r', encoding="utf-8") as jsonfile:
        captions = json.load(jsonfile)
    idcaption = random.randint(0, len(captions) - 1)
    idFile = random.randint(0, len(GFiles) - 1)
    idDir = GFiles[idFile][1]
    path = os.path.join(GDirs[idDir], GFiles[idFile][0])
    url = f"https://graph.facebook.com/v26.0/{page_id}/photos"
    params = {
        'access_token': app_token,
        "message": captions[idcaption]
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
                GPosted.append(GFiles[idFile][0])
                with open("Posted.json", "w") as file:
                    json.dump(GPosted, file)
                GFiles.pop(idFile)
            else:
                with open("log.txt", "a") as file:
                    file.write(str(datetime.datetime.now()) + str(result) + "\n")
            print("Files in queue: " + str(len(GFiles)))

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

def Main(OriginalDirectories):
    global GFiles, GDirs, GPosted
    with open("Posted.json", 'r') as jsonfile:
        GPosted = json.load(jsonfile)
    with open("BlackListed.json", 'r') as jsonfile:
        Blacklisted = json.load(jsonfile)  
    allFiles, GDirs = GetAllFiles(OriginalDirectories)
    print("Original Files: " + str(len(allFiles)))
    GFiles = CleanFiles(allFiles, GPosted, Blacklisted)
    print("Valid Files: " + str(len(GFiles)))

    PostImage()

    #Copy and paste for every time you want to post
    schedule.every().day.at("11:20").do(PostImage)  
    schedule.every().day.at("15:21").do(PostImage)
    schedule.every().day.at("19:22").do(PostImage)

    while True:
        schedule.run_pending()
        time.sleep(1)

Main(Directories)

#!/home/samuel/anaconda3/bin/python

import os
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from pydrive.files import FileNotDownloadableError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Script receives path to directory containing
# credentials and configuration files 
dir_path = Path(sys.argv[1])

cred_path = dir_path / "credentials.txt"
config_path = dir_path / "config.json"

#----Authenticate with Google----
gauth = GoogleAuth()

if os.path.isfile(cred_path) and os.path.isfile(config_path):
    gauth.LoadCredentialsFile(cred_path)
else:
    print("Missing config files!")

if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(cred_path)
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()

drive = GoogleDrive(gauth)

#----Mimetypes Dictionary for Converting Google Files----
mimetypes = {
     # Drive Document files as MS Word files.
    "application/vnd.google-apps.document": 
    ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
    ".docx"],
    # Drive Sheets files as MS Excel files.
    "application/vnd.google-apps.spreadsheet": 
    ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xlsx"],
    # Drive Presentation files as MS Powerpoint
    "application/vnd.google-apps.presentation":
    ["application/vnd.ms-powerpoint", ".ppt"], 
    # Drive Form files as PDFs
    "application/vnd.google-apps.form": ["application/pdf", ".pdf"]
}

#----Date and Configuration Values-----
today = datetime.now()
year = today.year
month = today.month
day = today.day
hour = today.hour
minute = today.minute
second = today.second

config = open(config_path, "r")
config_json = json.load(config)
backup_location = Path(config_json["location"])
folder_name = config_json["folder_name"]
date_extension = f"-{year}-{month:02d}-{day:02d}T{hour:02d}-{minute:02d}"
folder = folder_name + date_extension
save_path = backup_location / folder
os.makedirs(save_path)

failed_files = []


def ListFolder(parent, base_path, folder):
    file_list = drive.ListFile(
        {'q': "'{}' in parents and trashed=false".format(parent)}
        ).GetList()
 
    for f in file_list:
        file_path = ""
        save_path = base_path
        download_mimetype = None

        # Handle poorly named files
        name = f["title"].replace("/", "_")
        
        if f['mimeType'] in mimetypes:
            download_mimetype = mimetypes[f['mimeType']][0]
            extension = mimetypes[f['mimeType']][1]
            name = name + extension

        elif f['mimeType']=='application/vnd.google-apps.folder':
            save_path = save_path / f['title']
            os.makedirs(save_path)
            print("Type: folder")
            ListFolder(f['id'], save_path, folder)
            

        file_path = save_path / name
        print("Save Path: {}".format(save_path))
        print("File Path: {}".format(file_path))

        try:
            f.GetContentFile(file_path, mimetype=download_mimetype)
        except FileNotDownloadableError:
            if f['mimeType'] == "application/vnd.google-apps.form":
                print("Skipping Google Form: {}".format(f['title']))
                failed_files.append(f["title"])
            elif  f['mimeType'] != "application/vnd.google-apps.folder":
                print("FileNotDownloadableError on file {} {} {}".format(
                    f['title'], f['id'], f['mimeType']))
                sys.exit(0)
            continue
        except FileNotFoundError:
            print("File not found: \nSave path: {}\nFile path: {}".format(save_path, file_path))
            continue
        except pydrive.files.ApiRequestError:
            print("Cannot download file: API RequestError")
            failed_files.append(f["title"])
            continue

file_list = drive.ListFile(
    {'q': "'root' in parents and trashed=false"}
    ).GetList()

if not folder_name in [f['title'] for f in file_list]:
    print("No folder with that name!")
    sys.exit(0)

for f in file_list:
    if f['title'] == folder_name:
        folder_id = f['id']
        ListFolder(folder_id, save_path, folder)



# Create compressed archive and delete original directory
print("Creating zip archive. . .")
shutil.make_archive(save_path, 'zip', save_path)
print("Cleaning up. . .")
shutil.rmtree(save_path)
print("Done!")
print("\n")
print("Files skipped or failed: ")

for ff in failed_files:
    print(ff)
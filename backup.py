#!/home/samuel/anaconda3/bin/python

import os
import json
import shutil
import sys
from datetime import datetime
from pydrive.files import FileNotDownloadableError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

dir_path = sys.argv[1]

cred_path = os.path.join(dir_path, "credentials.txt")
config_path = os.path.join(dir_path, "config.json")

#----Authenticate with Google----
gauth = GoogleAuth()
gauth.LoadCredentialsFile(cred_path)

if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile(cred_path)

drive = GoogleDrive(gauth)

#----Mimetypes Dictionary for Converting Google Files----
mimetypes = {
     # Drive Document files as MS Word files.
    'application/vnd.google-apps.document': 
    ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
    ".docx"],
    # Drive Sheets files as MS Excel files.
    'application/vnd.google-apps.spreadsheet': 
    ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ".xlsx"],
    # Drive Presentation files as MS Powerpoint
    'application/vnd.google-apps.presentation':
    ['application/vnd.ms-powerpoint', ".ppt"], 
    # Drive Form files as PDFs
    'application/vnd.google-apps.form': 'application/pdf'
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
backup_location = config_json["location"]
folder_name = config_json["folder_name"]
date_extension = "-{}{}{}-{}{}{}".format(year, month, day, hour, minute, second)
folder = folder_name + date_extension
save_path = os.path.join(backup_location, folder_name + date_extension)
os.makedirs(save_path)


def ListFolder(parent, base_path, folder):
    file_list = drive.ListFile(
        {'q': "'{}' in parents and trashed=false".format(parent)}
        ).GetList()
 
    for f in file_list:
        file_path = ""
        save_path = base_path
        download_mimetype = None
        
        if f['mimeType'] in mimetypes:
            download_mimetype = mimetypes[f['mimeType']][0]
            extension = mimetypes[f['mimeType']][1]
            name = f['title'] + extension
            file_path = os.path.join(save_path, name)

        elif f['mimeType']=='application/vnd.google-apps.folder':
            save_path = os.path.join(save_path, f['title'])
            os.makedirs(save_path)
            print("Type: folder")
            ListFolder(f['id'], save_path, folder)
            
        else:
            name = f['title']
            file_path = os.path.join(save_path, name)

        print("Save Path: {}".format(save_path))
        print("File Path: {}".format(file_path))

        try:
            f.GetContentFile(file_path, mimetype=download_mimetype)
        except FileNotDownloadableError:
            print("Errror on file {} {} {}".format(
                f['title'], f['id'], f['mimeType']))
            continue

file_list = drive.ListFile(
    {'q': "'root' in parents and trashed=false"}
    ).GetList()
for f in file_list:
    if f['title'] == folder_name:
        folder_id = f['id']
        ListFolder(folder_id, save_path, folder)


# Create compressed archive and delete original directory
shutil.make_archive(save_path, 'zip', save_path)
shutil.rmtree(save_path)

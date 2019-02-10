# Google Drive Folder Backup

In general this is a simple script for locally backing up and compressing Google Drive folders. Specifically, this was created as a tool for the Factom community to allow members to automatically backup the Factom Governance documents. Distributed backups are a protection against single points of failure and malice. 

## Version
v0.1

## Getting Started

### Preqrequisites

* Python 3.0+
* Pydrive
* Linux OS (if utilizing systemd files)
* Access to Google Drive account where files are stored


### Setup
Install pydrive:

`pip install pydrive`

Set up systemd service and timer. 

1. Copy the `gdrive-backup.service` and `gdrive-backup.timer` files to `/etc/systemd/system/` or your preferred location for systemd files. 
2. Modify the `gdrive-backup.service` and `gdrive-backup.timer` files as follows:
    for `gdrive-backup.service`:
    * Replace "USERNAME" with your system's username to run the program under
    * Replace "/path/to/gdrive-backup/backup.py" with the correct path to the Python script file
    * Replace "/path/to/config and credential files/" with the path to where you store the configuration JSON file and where you will store the GAuth credential files. 
    * Replace `OnCalendar=weekly` in `gdrive-backup.timer` with your preferred frequency for backups: e.g. `daily` or `monthly`. For more information on systemd and systemd timers see: https://wiki.archlinux.org/index.php/systemd. 
3. Add both files to your desired location for systemd files on your system. Run `systemctl enable gdrive-backup.timer` and `systemctl start gdrive-backup.timer`. 

Set up `config.json`.

1. Set "location" to the desired path for where the backup file should go.
2. Set "folder_name" to the name of the Google Drive folder to download.

Obtain Google OAuth 2.0 credentials by visting https://console.developers.google.com/ signed into the Google account you will use. Create credentials and download the "client_secrets.json" file to the same location that you store your `config.json` file. 

## Running
The first time the program is run it will open a webpage and ask you to sign into your Google account. When you authorize the program's access by signing into an account it will then download the `credentials.txt` file which you should place in the same location as the `config.json` and `client_secrets.txt` files. 

The program can be run manually by `python backup.py /path-to-credentials/` or `systemctl start gdrive-backup.service`.

## Contact

Contact Samuel Vanderwaal for questions.

samuel.vanderwaal@gmail.com

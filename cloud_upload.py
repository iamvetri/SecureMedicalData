from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def upload_to_drive(filepath):
    gauth = GoogleAuth()

    # Try loading saved credentials
    gauth.LoadCredentialsFile("token.pickle")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("token.pickle")

    drive = GoogleDrive(gauth)
    upload_file = drive.CreateFile({'title': os.path.basename(filepath)})
    upload_file.SetContentFile(filepath)
    upload_file.Upload()

    return upload_file['alternateLink']

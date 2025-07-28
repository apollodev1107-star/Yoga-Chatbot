from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'backend/credentials.json'

def download_pdfs_from_drive(folder_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf'",
        pageSize=100,
        fields="files(id, name)").execute()

    files = results.get('files', [])
    local_paths = []

    os.makedirs("downloads", exist_ok=True)

    for file in files:
        file_path = f"downloads/{file['name']}"
        request = service.files().get_media(fileId=file['id'])
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        local_paths.append(file_path)

    return local_paths

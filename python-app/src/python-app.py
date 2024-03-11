import os

import mysql.connector 
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
TOKEN_JSON_FILE = 'token.json'

CLIENT_SECRET_FILE = '/Users/issei.hosoda/Documents/docker-kadai/python-app/src/client_secret.com.json'
SPREADSHEET_ID = '1BESKZh6g_UCrUALFFZ3Kwq7j6eyQPO0VBibRUwXcwkU'
RANGE_NAME = 'dummy!A2:H501'

#Google Sheets APIを使用してスプレッドシートからデータを取得する関数
def get_questionnaire():
    credentials = None
    if os.path.exists(TOKEN_JSON_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_JSON_FILE, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(TOKEN_JSON_FILE, 'w') as token:
            token.write(credentials.to_json())

    service = build('sheets', 'v4', credentials=credentials)
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()

    return result.get('values', [])

def insert_data(questionnaire_data):
    conn = None
    try:
        conn = mysql.connector.connect(
            user='root',
            password='Hoso-8805-da',
            host='localhost',
            database='rancher'
            )

        c = conn.cursor()

        sql = 'insert into rancher.questionnaire values (%s, %s, %s, %s, %s, %s, %s, %s)'
        c.executemany(sql, questionnaire_data)
        conn.commit()

        c.close()

    except Exception as e:
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def main():
    res = get_questionnaire()
    insert_data(res)

if __name__ == "__main__":
    main()
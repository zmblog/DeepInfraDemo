#!pip install OpenAI
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import requests
from openai import OpenAI
from google.colab import files
uploaded = files.upload()
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID= "1eBfILvevOykkylb8fvAD2ag3UpSVWjqINuoDhGBdxEI" #REPLACE
BASE_URL = 'https://api.deepinfra.com/v1/openai'
API_KEY="Bclq2G5sIJWoogyGIMabTFVnr39aMQSd", #this api key probably doesnt work anymore.
os.environ['BROWSER'] = '/usr/bin/google-chrome'

def get_google_docs_content():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)
    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_content = read_paragraph_element(document.get('body').get('content'))
    return doc_content

def read_paragraph_element(elements):
    text = ""
    for element in elements:
        if 'paragraph' in element:
            for elem in element['paragraph']['elements']:
                if 'textRun' in elem:
                    text += elem['textRun']['text']['content']
    return text

def ask_question_about_document(document_text, question):
    data = {
          "model": "meta-llama/Meta-Llama-3-70B-Instruct",  # Adjust model according to what's available on your proxy API
          "prompt": f"Document: {document_text}\n\nQuestion: {question}",
          "max_tokens": 150,
          "temperature": 0.7
    }
    headers = {
          "Authorization": f"Bearer {API_KEY}",
          "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
    return response.json()

document_text = get_google_docs_content()
question = "What is the main topic of the document?"  # Example question

# Send the question to the custom API endpoint
try:
    response = ask_question_about_document(document_text, question)
    print(response['choices'][0]['message']['content'])  # Adjust depending on the exact response structure
except Exception as e:
    print("An error occurred:", e)

import datetime
import os
import time
import playsound
import speech_recognition as sr
from gtts import gTTS
import webbrowser
import openai
import wikipedia
import tkinter as tk
from tkinter import messagebox
from threading import Thread

from dotenv import load_dotenv
load_dotenv()


openai.api_key = os.getenv("OPENAI_API_KEY")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def speak(text):
    print("Assistant:", text)
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
            print("You said:", said)
        except Exception as e:
            print("Exception:", str(e))
    return said.lower()

def authenticate_google():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds)
    return service

def get_events(n, service):
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        speak("Getting your upcoming events.")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=n,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            speak("No upcoming events found.")
            return
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            speak(f"{summary} at {start}")
    except HttpError as error:
        print("Error:", error)
        speak("Sorry, I could not fetch events.")

def open_calendar_in_chrome():
    speak("Opening your Google Calendar in Chrome.")
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
    url = "https://calendar.google.com"
    webbrowser.get(chrome_path).open(url)

def answer_general_question(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        answer = response["choices"][0]["message"]["content"]
        speak(answer)
    except Exception as e:
        try:
            speak("Let me check Wikipedia.")
            summary = wikipedia.summary(query, sentences=2)
            speak(summary)
        except:
            speak("Sorry, I couldn't find an answer.")

def handle_command():
    query = get_audio()

    if "get events" in query:
        service = authenticate_google()
        get_events(5, service)
    elif "open calendar" in query:
        open_calendar_in_chrome()
    elif "exit" in query or "quit" in query:
        speak("Goodbye!")
        app.destroy()
    else:
        answer_general_question(query)

# GUI Setup
def start_listening():
    speak("Hello! You can say things like get events, open calendar, or ask any question.")
    Thread(target=handle_command).start()

app = tk.Tk()
app.title("Smart Voice Assistant")
app.geometry("400x300")
app.configure(bg="#f0f0f0")

label = tk.Label(app, text="Click the button and speak", font=("Arial", 14), bg="#f0f0f0")
label.pack(pady=40)

btn = tk.Button(app, text="Start Listening", font=("Arial", 14), command=start_listening, bg="#4caf50", fg="white", padx=20, pady=10)
btn.pack()

exit_btn = tk.Button(app, text="Exit", font=("Arial", 12), command=app.quit, bg="#f44336", fg="white", padx=10, pady=5)
exit_btn.pack(pady=20)

app.mainloop()





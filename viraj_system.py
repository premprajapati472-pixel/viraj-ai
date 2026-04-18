import pyttsx3
import speech_recognition as sr
import os
import sys
import webbrowser
import requests
import time
import subprocess

# --- CONFIGURATION ---
PB_TOKEN = "o.JA7lF7bR4IZkRDoGsappsyDVNZrSXlk2" 

# --- VOICE SETUP ---
engine = pyttsx3.init('sapi5')
def speak(text):
    print(f"Viraj: {text}")
    engine.say(text)
    engine.runAndWait()

# --- UNIVERSAL CLOSE LOGIC (Apps ko band karne ke liye) ---
def close_app(app_name):
    # Common apps ki process list
    apps_dict = {
        "chrome": "chrome.exe",
        "browser": "chrome.exe",
        "notepad": "notepad.exe",
        "whatsapp": "WhatsApp.exe",
        "youtube": "chrome.exe", # YouTube browser mein chalta hai
        "vlc": "vlc.exe",
        "tally": "tally.exe"
    }
    
    process_name = apps_dict.get(app_name.lower(), app_name.lower() + ".exe")
    try:
        os.system(f"taskkill /f /im {process_name}")
        speak(f"{app_name} band kar diya gaya hai.")
    except:
        speak(f"Maaf kijiye, main {app_name} ko band nahi kar pa raha hoon.")

# --- UNIVERSAL OPEN LOGIC (Sab kuch kholne ke liye) ---
def execute_task(query):
    if not query: return False
    
    # --- BAND KARNE KA COMMAND ---
    if "band karo" in query or "close" in query:
        app_to_close = query.replace("band karo", "").replace("close", "").replace("viraj", "").strip()
        close_app(app_to_close)
        return True

    # --- KHOLNE KA COMMAND ---
    if "kholo" in query or "open" in query:
        app_to_open = query.replace("kholo", "").replace("open", "").replace("viraj", "").strip()
        
        # Special case: YouTube
        if "youtube" in app_to_open:
            speak("YouTube khol raha hoon.")
            webbrowser.open("https://www.youtube.com")
        
        # Special case: WhatsApp
        elif "whatsapp" in app_to_open:
            speak("WhatsApp open kar raha hoon.")
            webbrowser.open("https://web.whatsapp.com") # Ya agar app hai toh os.startfile use karein
            
        # Common System Apps (Notepad, Chrome etc)
        elif "notepad" in app_to_open:
            os.system("start notepad")
        elif "chrome" in app_to_open:
            os.system("start chrome")
            
        # Any other website
        else:
            speak(f"{app_to_open} dhoond kar khol raha hoon.")
            webbrowser.open(f"https://www.google.com/search?q={app_to_open}&btnI")
        return True

    return False

# --- PUSHBULLET REMOTE LISTENER ---
def check_remote_command():
    try:
        url = "https://api.pushbullet.com/v2/pushes?limit=1"
        resp = requests.get(url, auth=(PB_TOKEN, ''))
        if resp.status_code == 200:
            pushes = resp.json().get('pushes', [])
            if pushes:
                latest = pushes[0]
                if time.time() - latest['created'] < 10: # Only if message is fresh
                    return latest.get('body', '').lower()
    except: pass
    return None

# --- SPEECH RECOGNITION ---
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n--- Viraj Listening ---")
        r.adjust_for_ambient_noise(source, duration=0.8)
        r.energy_threshold = 4000
        try:
            audio = r.listen(source, timeout=3, phrase_time_limit=4)
            return r.recognize_google(audio, language='hi-IN').lower()
        except: return "none"

# --- MAIN ENGINE ---
if __name__ == "__main__":
    speak("Viraj System 2.0 active. Balram sir, main aapke control mein hoon.")
    
    while True:
        # 1. Phone Command
        remote_q = check_remote_command()
        if remote_q: 
            print(f"Remote: {remote_q}")
            execute_task(remote_q)

        # 2. Voice Command
        voice_q = takeCommand()
        if voice_q != "none":
            print(f"Voice: {voice_q}")
            if "exit" in voice_q or "band ho jao" in voice_q:
                speak("Theek hai sir. System off ho raha hai.")
                os._exit(0)
            execute_task(voice_q)
        
        time.sleep(0.2)
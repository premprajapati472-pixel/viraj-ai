import time
import os
import psutil
import pyttsx3
import pyautogui
import datetime
from pushbullet import Pushbullet
from google import genai

# --- CONFIGURATION ---
PB_API_KEY = "o.JA7lF7bR4IZkRDoGsappsyDVNZrSXlk2" 
pb = Pushbullet(PB_API_KEY)
client = genai.Client(api_key="AIzaSyCKS2Jvj95eqBPOePfIDQiFbKlSRAMWe90") 

SECRET_PIN = "7860"
engine = pyttsx3.init()

def speak(text):
    print(f"Viraj: {text}")
    engine.say(text)
    engine.runAndWait()

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # File path sahi rakhein
    with open(r"D:\python\viraj_diary.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def send_screenshot(msg="System Screenshot"):
    shot_path = r"D:\python\current_screen.png"
    pyautogui.screenshot(shot_path)
    try:
        with open(shot_path, "rb") as f:
            file_data = pb.upload_file(f, "viraj_screen.png")
        pb.push_file(**file_data)
        pb.push_note("Viraj Update", msg)
        if os.path.exists(shot_path):
            os.remove(shot_path)
    except:
        pass

def get_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: return "Good Morning Balram Sir!"
    elif 12 <= hour < 17: return "Good Afternoon Balram Sir!"
    elif 17 <= hour < 21: return "Good Evening Balram Sir!"
    else: return "Good Night Balram Sir!"

def auto_check_and_greet():
    greeting = get_greeting()
    speak(greeting)
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent()
    
    report = f"{greeting}\nSystem Status Report:\n- Battery: {battery.percent}%\n- CPU Load: {cpu}%\n"
    
    issues = []
    if battery.percent < 30 and not battery.power_plugged:
        issues.append("Sir, battery kam hai.")
    if cpu > 80:
        issues.append("Sir, laptop garam ho raha hai.")
    
    if issues:
        warning_msg = " aur ".join(issues)
        speak(f"Sir, ek dikkat hai. {warning_msg}. Kya main ise solve karun?")
        report += f"\nALERTS: {warning_msg} ⚠️"
    else:
        speak("Sab kuch normal hai sir. System ekdum mast chal raha hai.")
        report += "\nSystem status: Healthy ✅"

    pb.push_note("Viraj Startup Report", report)
    send_screenshot("Startup Status")
    log_event("Startup greeting aur report bhej di gayi.")

def process_remote_command(msg):
    # Har message ko diary mein likhega, chahe PIN ho ya na ho
    log_event(f"Raw Message Received: {msg}")
    
    if not msg.startswith(SECRET_PIN): return
    
    # PIN hata kar command nikalna
    cmd = msg.replace(SECRET_PIN, "").strip().lower()
    log_event(f"Action Taken for Command: {cmd}")

    # 1. System Update/Report
    if "system update" in cmd or "report" in cmd:
        battery = psutil.sensors_battery()
        cpu = psutil.cpu_percent()
        update_text = f"Battery: {battery.percent}% | CPU: {cpu}%"
        pb.push_note("Viraj Report", update_text)
        send_screenshot(update_text)

    # 2. Chrome Band Karo
    elif "chrome band karo" in cmd or "close chrome" in cmd:
        speak("Ji sir, Chrome band kar raha hoon.")
        os.system("taskkill /f /im chrome.exe")
        pb.push_note("Viraj", "Chrome band kar diya gaya hai.")

    # 3. Flexible Website Opening (Tata Steel, Amazon etc.)
    elif "kholo" in cmd or "open" in cmd:
        site = ""
        if "tata steel" in cmd: site = "https://www.tatasteel.com"
        elif "amazon" in cmd: site = "https://www.amazon.in"
        elif "google" in cmd: site = "https://www.google.com"
        elif "youtube" in cmd: site = "https://www.youtube.com"
        
        if site:
            speak(f"{cmd.split('kholo')[0]} khol raha hoon.")
            # start chrome command fix
            os.system(f'start chrome "{site}"')
            send_screenshot(f"{site} khul gaya hai.")
        else:
            # Agar koi unknown site hai to seedhe google search
            query = cmd.replace("kholo", "").replace("open", "").strip()
            os.system(f'start chrome "https://www.google.com/search?q={query}"')

    # 4. Cleanup
    elif "clean" in cmd:
        speak("Sir, temporary files saaf kar raha hoon.")
        os.system(r'del /q/f/s %TEMP%\*')
        pb.push_note("Viraj", "Cleanup complete.")

    # 5. Flutter Coding
    elif "flutter" in cmd:
        speak("Flutter code generate kar raha hoon.")
        prompt = f"Write Flutter code for: {cmd}"
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        with open(r"D:\python\viraj_flutter_output.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        pb.push_note("Viraj", "Code file mein save ho gaya hai.")

# --- MAIN ENGINE ---
def main():
    log_event("Viraj System Online.")
    auto_check_and_greet()
    
    last_id = ""
    try:
        initial = pb.get_pushes()
        if initial: last_id = initial[0]['iden']
    except: pass

    while True:
        try:
            pushes = pb.get_pushes()
            if pushes:
                # ... baki code ...
        except Exception as e:
            # Agar rate limit error aaye to thoda zyada wait karein
            if "ratelimited" in str(e).lower():
                log_event("Pushbullet Rate Limit Hit. Waiting for 2 minutes...")
                time.sleep(120) # 2 minute ka break
            else:
                log_event(f"Error Loop: {e}")
                time.sleep(10) 

        # Ise 2 se badha kar 7-10 second kar dein
        time.sleep(10) # Refresh rate fast kiya gaya hai

if __name__ == "__main__":
    main()
import pyttsx3
import time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
TOKEN = "8530203551:AAFKM2_ehvHxdhWG2Od1q7LRG4U5zx_urYo"
MY_ID = 1910654363
PIN = "7860"

# --- ENGINE SETUP ---
engine = pyttsx3.init()
driver = None # Browser handle karne ke liye global variable

def speak(text):
    print(f"Viraj: {text}")
    engine.say(text)
    engine.runAndWait()

def get_driver():
    """Naye Chrome 147 ke liye driver setup"""
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--remote-allow-origins=*")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # WebDriver Manager auto-update karega driver ko
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

async def handle_viraj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver
    user_msg = update.message.text.lower().strip()
    chat_id = update.effective_chat.id

    # Security check
    if chat_id != MY_ID:
        return

    if PIN in user_msg:
        cmd = user_msg.replace(PIN, "").strip()
        reply = ""

        try:
            # Action 1: Site Kholna
            if "kholo" in cmd:
                site_name = cmd.replace("kholo", "").strip()
                if "." not in site_name:
                    url = f"https://www.google.com/search?q={site_name}"
                else:
                    url = f"https://{site_name}"
                
                browser = get_driver()
                browser.get(url)
                reply = f"Sir, maine {site_name} khol diya hai."

            # Action 2: Site Band Karna
            elif "band karo" in cmd:
                if driver:
                    driver.quit()
                    driver = None
                    reply = "Sir, browser band kar diya gaya hai."
                else:
                    reply = "Sir, koi browser chalu nahi hai."

            # Action 3: Report (Simple version)
            elif "report" in cmd:
                reply = "System status: All systems nominal. Chrome v147 connected."

            else:
                reply = "Viraj: Command samajh nahi aayi, Sir."

        except Exception as e:
            reply = f"Error: {str(e)}"
            if "session not created" in reply:
                reply = "Error: Kripya apna purana Chrome band karein aur fir command dein."

        speak(reply)
        await update.message.reply_text(reply)

def main():
    print("Viraj AI Pro is Active (Chrome v147 Support Enabled)...")
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_viraj))
        app.run_polling()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    main()
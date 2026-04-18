import os
import psutil
import getpass # Aapka PC username nikalne ke liye
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class VirajPlugins:
    windows_memory = {}

    @staticmethod
    def get_system_report():
        battery = psutil.sensors_battery()
        cpu = psutil.cpu_percent()
        return f"🔋 Battery: {battery.percent}%\n💻 CPU Load: {cpu}%"

    @staticmethod
    def open_site_smart(site_name):
        site_key = site_name.lower().strip()
        username = getpass.getuser() # Aapke PC ka username automatically le lega
        
        sites = {
            "tata steel": "https://www.tatasteel.com",
            "amazon": "https://www.amazon.in",
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com"
        }
        
        target_url = sites.get(site_key, f"https://www.google.com/search?q={site_key}")

        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            
            # --- ASLI CHROME PROFILE USE KARNE KA LOGIC ---
            # Ye rasta Viraj ko aapke asli Chrome data tak le jayega
            user_data_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
            chrome_options.add_argument(f"user-data-dir={user_data_dir}")
            
            # Profile 1 ya Default (Aap check kar sakte hain, aksar Default hota hai)
            chrome_options.add_argument("profile-directory=Default") 
            
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(target_url)
            
            VirajPlugins.windows_memory[site_key] = driver
            return f"Sir, {site_name} aapke asli Chrome profile mein khol di hai."
        except Exception as e:
            # Agar Chrome pehle se khula hai, toh error aa sakta hai
            return f"Sir, Error: Kripya apna normal Chrome band karke command dein, ya path check karein. Error: {e}"

    @staticmethod
    def close_specific_site(site_name):
        site_key = site_name.lower().strip()
        if site_key in VirajPlugins.windows_memory:
            try:
                driver = VirajPlugins.windows_memory[site_key]
                driver.quit()
                del VirajPlugins.windows_memory[site_key]
                return f"Sir, {site_name} band kar di gayi hai."
            except:
                if site_key in VirajPlugins.windows_memory: del VirajPlugins.windows_memory[site_key]
                return "Sir, window pehle hi band ho chuki hai."
        else:
            return f"Sir, '{site_name}' meri memory mein nahi hai."

    @staticmethod
    def clean_system():
        os.system(r'del /q/f/s %TEMP%\*')
        return "Sir, junk files saaf kar di hain."
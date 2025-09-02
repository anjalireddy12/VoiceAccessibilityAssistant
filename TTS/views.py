from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import os
import subprocess
import shutil
import datetime
import requests
import urllib
import pyttsx3
import pyautogui
import webbrowser
import speech_recognition as sr
import pyjokes
import pywhatkit
from bs4 import BeautifulSoup
from django.shortcuts import render

# ========== CONFIGURATION ==========
GEMINI_API_KEY = "AIzaSyD5eAYRj9Db29f4KCzCv5CMxEh5K2GIdwY"
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}'
WEATHER_API_KEY = "0d7f551109ba7c4d548985f2e8cea6f8"

system_apps = {
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "files": r"explorer.exe",
    "v s code": r"C:\Users\selen\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "camera": "start microsoft.windows.camera:",
    "microsoft store": "start ms-windows-store:",
    "settings": "start ms-settings:",
    "spotify": r"C:\Users\selenAppData\Roaming\Spotify\Spotify.exe",
    "whatsapp": r"C:\Users\selen\AppData\Local\WhatsApp\WhatsApp.exe"
}

web_links = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://www.reddit.com",
    "spotify": "https://open.spotify.com",
    "stackoverflow": "https://stackoverflow.com",
    "twitter": "https://twitter.com",
    "facebook": "https://facebook.com"
}

engine = pyttsx3.init()
engine.setProperty("rate", 150)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass

def get_path(location):
    user = os.environ['USERPROFILE']
    one = os.path.join(user, 'OneDrive')
    folders = {
        "desktop": "Desktop",
        "documents": "Documents",
        "downloads": "Downloads",
        "pictures": "Pictures",
        "gallery": "Pictures",
        "music": "Music",
        "videos": "Videos"
    }
    name = folders.get(location.lower().strip(), "Desktop")
    path = os.path.join(user, name)
    alt = os.path.join(one, name)
    return path if os.path.exists(path) else alt if os.path.exists(alt) else user

def gemini_generate(prompt):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
        if res.status_code == 200:
            candidates = res.json().get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "⚠️ No response.")
            return "⚠️ Empty response."
        else:
            return f"⚠️ Gemini error: {res.text}"
    except Exception as e:
        return f"⚠️ Gemini exception: {e}"

def open_app(app_name):
    app_name = app_name.lower()
    if app_name in system_apps:
        path = system_apps[app_name]
        try:
            subprocess.Popen([path])
            speak(f"Opening {app_name}")
            return True
        except Exception as e:
            speak(f"Failed to open {app_name}: {e}")
            return False
    else:
        # Try default system command for calculator
        if app_name == "calculator":
            try:
                subprocess.Popen("calc.exe")
                speak("Opening calculator")
                return True
            except Exception as e:
                speak(f"Failed to open calculator: {e}")
                return False
    speak(f"App {app_name} not found.")
    return False

def open_file_or_folder(target, location="desktop", app=None):
    base_path = get_path(location)
    # Search folders top-level only
    for root, dirs, files in os.walk(base_path):
        for dir in dirs:
            if dir.lower() == target.lower():
                full = os.path.join(root, dir)
                try:
                    if app and app in system_apps:
                        app_path = system_apps[app]
                        subprocess.Popen([app_path, full])
                        speak(f"Opened folder {target} in {app}")
                    else:
                        os.startfile(full)
                        speak(f"Opened folder {target}")
                    return True
                except Exception as e:
                    speak(f"Could not open folder: {e}")
                    return False
        break
    # Search files top-level only
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower() == target.lower() or file.lower().startswith(target.lower()):
                full = os.path.join(root, file)
                try:
                    if app and app in system_apps:
                        app_path = system_apps[app]
                        subprocess.Popen([app_path, full])
                        speak(f"Opened file {target} in {app}")
                    else:
                        os.startfile(full)
                        speak(f"Opened file {target}")
                    return True
                except Exception as e:
                    speak(f"Could not open file: {e}")
                    return False
        break
    speak(f"{target} does not exist in {location}.")
    return False

def create_folder(folder, location="desktop"):
    path = get_path(location)
    full = os.path.join(path, folder)
    try:
        if os.path.exists(full):
            speak(f"Folder {folder} already exists.")
            return False
        os.makedirs(full)
        speak(f"Created folder {folder}")
        return True
    except Exception as e:
        speak(f"Failed to create folder: {e}")
        return False

def create_file(filename, location="desktop"):
    path = get_path(location)
    full = os.path.join(path, filename)
    try:
        if os.path.exists(full):
            speak(f"File {filename} already exists.")
            return False
        with open(full, "w") as f:
            f.write("Voice created file.")
        speak(f"Created file {filename}")
        return True
    except Exception as e:
        speak(f"Failed to create file: {e}")
        return False

def delete_item(item, location="desktop"):
    path = get_path(location)
    for root, dirs, files in os.walk(path):
        for name in files + dirs:
            if name.lower() == item.lower():
                full_path = os.path.join(root, name)
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    speak(f"Deleted {item}.")
                    return True
                except Exception as e:
                    speak("Couldn't delete the item.")
                    return False
        break
    speak("Item not found to delete.")
    return False

def get_weather_google(city="Hyderabad"):
    try:
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(city)}+weather"
        headers = {"User-Agent": "Mozilla/5.0"}
        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        temp = soup.find("span", attrs={"id": "wob_tm"})
        wind = soup.find("span", attrs={"id": "wob_ws"})
        desc = soup.find("span", attrs={"id": "wob_dc"})
        if temp and wind and desc:
            temp_val = temp.text
            wind_val = wind.text
            desc_val = desc.text
            weather_str = f"{city} weather: {temp_val}°C, {desc_val}, wind {wind_val}"
            speak(f"The temperature is {temp_val} degrees Celsius with {desc_val} and wind {wind_val}.")
            return weather_str
        else:
            speak("Couldn't fetch weather info.")
            return "Couldn't fetch weather info."
    except Exception as e:
        speak("Couldn't fetch weather info.")
        return "Couldn't fetch weather info."

def result2(request):
    recognized_text = ""
    generated_code = ""
    suggestion_prompt = ""
    ask_app = False
    pending_target = ""
    pending_location = ""

    if request.method == "POST":
        try:
            recog = sr.Recognizer()
            with sr.Microphone() as source:
                recog.adjust_for_ambient_noise(source)
                audio = recog.listen(source, timeout=5)
            recognized_text = recog.recognize_google(audio).lower().strip()

            # Handle interactive follow-up for app choice
            if "pending_open" in request.session:
                pending = request.session["pending_open"]
                app = recognized_text.strip()
                target = pending["target"]
                location = pending["location"]
                opened = open_file_or_folder(target, location, app)
                if not opened:
                    suggestion_prompt = f"{target} does not exist in {location}."
                del request.session["pending_open"]
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": False
                })

            # --- ADD THIS BLOCK: OPEN SYSTEM APP ---
            if recognized_text.startswith("open "):
                app_name = recognized_text.replace("open", "").replace("app", "").strip()
                # If it's a known app, open it and return
                if open_app(app_name):
                    return render(request, "result2.html", {
                        "recognized_text": recognized_text,
                        "generated_code": generated_code,
                        "suggestion_prompt": suggestion_prompt,
                        "ask_app": ask_app,
                    })
            # ----------------------------------------

            # Code generation
            if recognized_text.startswith("generate code"):
                prompt = recognized_text.replace("generate code", "").strip()
                if prompt:
                    generated_code = gemini_generate(f"Generate a single Python code for: {prompt} without any explanation")
                    suggestion_prompt = "💡 Try: 'Generate code to check prime number.'"
                    speak("Here is the code generated.")
                else:
                    generated_code = "⚠️ Specify what code to generate."
                    speak(generated_code)

            # Gemini joke
            elif "tell me a joke" in recognized_text:
                joke = gemini_generate("Tell me a short, funny joke.")
                speak(joke)
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": ask_app,
                })

            # Pyjokes joke
            elif "crack a joke" in recognized_text:
                joke = pyjokes.get_joke()
                speak(joke)
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": ask_app,
                })

            # Weather
            elif "weather" in recognized_text:
                get_weather_google("Hyderabad")
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": ask_app,
                })

            # Time
            elif "time" in recognized_text:
                now = datetime.datetime.now().strftime('%I:%M %p')
                speak(f"The time is {now}")
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": ask_app,
                })

            # Screenshot
            elif "screenshot" in recognized_text:
                img = pyautogui.screenshot()
                img.save(os.path.join(os.getcwd(), "screenshot.png"))
                speak("Screenshot saved.")

            # Note or reminder
            elif "note" in recognized_text or "reminder" in recognized_text:
                speak("What should I write?")
                recog = sr.Recognizer()
                with sr.Microphone() as source:
                    recog.adjust_for_ambient_noise(source)
                    note_audio = recog.listen(source)
                content = recog.recognize_google(note_audio)
                filename = "notes.txt" if "note" in recognized_text else "reminders.txt"
                with open(filename, "a") as f:
                    f.write(content + "\n")
                speak("Saved.")

            # Play on YouTube
            elif recognized_text.startswith("play") and "spotify" not in recognized_text:
                song = recognized_text.replace("play", "").strip()
                pywhatkit.playonyt(song)
                speak(f"Playing {song} on YouTube.")

            # Play on Spotify
            elif recognized_text.startswith("play") and "spotify" in recognized_text:
                song = recognized_text.replace("play", "").replace("on spotify", "").strip()
                url = f"https://open.spotify.com/search/{urllib.parse.quote_plus(song)}"
                webbrowser.open(url)
                speak(f"Searching for {song} on Spotify.")

            # Open file or folder (interactive)
            import re
            match = re.match(r"open (folder|file) (.+?)(?: from ([\w\s]+))?(?: on (\w+))?$", recognized_text)
            if match:
                kind, target, location, app = match.groups()
                target = target.strip()
                location = location.strip() if location else "desktop"
                app = app.strip() if app else None
                if not app:
                    speak("Where should I open it? For example, say vscode, notepad, excel, word, or explorer.")
                    request.session["pending_open"] = {"target": target, "location": location}
                    ask_app = True
                    pending_target = target
                    pending_location = location
                else:
                    opened = open_file_or_folder(target, location, app)
                    if not opened:
                        suggestion_prompt = f"{target} does not exist in {location}."
                return render(request, "result2.html", {
                    "recognized_text": recognized_text,
                    "generated_code": generated_code,
                    "suggestion_prompt": suggestion_prompt,
                    "ask_app": ask_app,
                    "pending_target": pending_target,
                    "pending_location": pending_location,
                })

            # Create folder
            elif recognized_text.startswith("create folder"):
                folder = recognized_text.replace("create folder", "").strip()
                create_folder(folder)

            # Create file
            elif recognized_text.startswith("create file"):
                filename = recognized_text.replace("create file", "").strip()
                create_file(filename)

            # Delete item
            elif recognized_text.startswith("delete"):
                item = recognized_text.replace("delete", "").strip()
                delete_item(item)

            # Exit
            elif "exit" in recognized_text or "stop" in recognized_text:
                speak("Goodbye")

            # Open web links (only explicit)
            elif any(site in recognized_text for site in web_links):
                for site in web_links:
                    if site in recognized_text:
                        webbrowser.open(web_links[site])
                        speak(f"Opened {site}")
                        break

            # Google search fallback
            else:
                speak(f"Searching the web for {recognized_text}")
                url = f"https://www.google.com/search?q={urllib.parse.quote_plus(recognized_text)}"
                webbrowser.open(url)

        except sr.UnknownValueError:
            recognized_text = "🎧 Could not understand audio."
        except sr.RequestError:
            recognized_text = "⚠️ Speech recognition service unavailable."
        except Exception as e:
            recognized_text = f"⚠️ Internal error: {str(e)}"

    else:
        recognized_text = "Press the microphone button and speak."

    return render(request, "result2.html", {
        "recognized_text": recognized_text,
        "generated_code": generated_code,
        "suggestion_prompt": suggestion_prompt,
        "ask_app": ask_app,
        "pending_target": pending_target,
        "pending_location": pending_location,
    })

































def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    extracted_text = ""
    for page in doc:
        extracted_text += page.get_text("text")
    doc.close()
    return extracted_text.strip()

def extract_text_from_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text.strip()


def home(request):
    return render(request, 'home.html')


def result(request):
    if request.method == 'POST':
        input_type = request.POST.get('input_type')
        extracted_text = ""
        if input_type == 'text':
            extracted_text = request.POST.get('input_text', '').strip()
            if not extracted_text:
                extracted_text = "No text was provided."
        elif input_type == 'pdf' and request.FILES.get('pdf_file'):
            pdf_file = request.FILES['pdf_file']
            file_path = default_storage.save('temp/' + pdf_file.name, pdf_file)
            abs_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            try:
                extracted_text = extract_text_from_pdf(abs_file_path)
            except Exception as e:
                extracted_text = f"Error extracting text: {e}"
            if os.path.exists(abs_file_path):
                os.remove(abs_file_path)
        elif input_type == 'image' and request.FILES.get('image_file'):
            image_file = request.FILES['image_file']
            file_path = default_storage.save('temp/' + image_file.name, image_file)
            abs_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            try:
                extracted_text = extract_text_from_image(abs_file_path)
            except Exception as e:
                extracted_text = f"Error extracting text: {e}"
            if os.path.exists(abs_file_path):
                os.remove(abs_file_path)
        else:
            extracted_text = "No valid input provided."
        return render(request, 'result.html', {'extracted_text': extracted_text})
    return redirect('home')



def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('num1')
        password = request.POST.get('num2')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('result2')
    return render(request,'login.html')
    
def registerpage(request):
    if request.method == 'POST':
        username = request.POST.get('num1')
        password = request.POST.get('num2')
        conform = request.POST.get('num3')
        if password != conform:
            return render(request,'register.html',{'result':'ERROR'})
        user=User.objects.create_user(username=username,password=password)
        return redirect('login')
    return render(request,'register.html')
def home(request):
    return render (request,'home.html')









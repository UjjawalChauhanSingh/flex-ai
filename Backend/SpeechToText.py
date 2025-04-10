from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os 
import mtranslate as mt
from rich import print


env_vars = dotenv_values(".env")

InputLanguage = env_vars.get('InputLanguage')

# Define HTML code for speech recognition interface
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace language setting in HTML with InputLanguage
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")


project_dir = r"C:\Users\ujjaw\OneDrive\Desktop\JARVIS"
html_path = os.path.join(project_dir, "Data", "Html", "Voice.html")

# Make sure the directory exists, and create it if necessary
os.makedirs(os.path.dirname(html_path), exist_ok=True)


with open(html_path, "w") as f:
    f.write(HtmlCode)

# Get the current directory
current_dir = os.getcwd()

# Link to the local HTML file
Link = f"file:///{html_path}"


service = Service(ChromeDriverManager().install())
chrome_options = Options()
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(service=service, options=chrome_options)

# Define temporary directory path for storing status
TempDirPath = os.path.join(current_dir, "Frontend", "Files")

# Function to set assistant status
def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as f:
        f.write(Status)

# Function to modify the query
def QueryModifier(Query: str):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "when", "where", "who", "why", "how", "which",
                      "whom", "whose", "can you", "could you", "would you", "will you",
                      "may you", "might you", "should you", "is it", "are you", "am i",
                      "do you", "does it", "did you", "have you", "has it", "had you",
                      "will it", "would it", "can i", "could i", "may i", "might i",
                      "should i", "is there", "are there", "was there", "were there",
                      "has there", "have there", "had there", "will there", "would there",
                      "can there", "could there", "may there", "might there", "should there",
                      "is this", "are these", "was this", "were these", "has this",]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

# Function for universal translation
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Main function for speech recognition
def SpeechRecognition():
    driver.get(Link)

    driver.find_element(by = By.ID, value = "start").click()
    print("Listening...")

    while True:
        try:
            Text = driver.find_element(by = By.ID, value = "output").text

            if Text:
                driver.find_element(by = By.ID, value = "end").click()

                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return f"\n{QueryModifier(UniversalTranslator(Text))}\n"
        
        except Exception as e:
            pass

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)

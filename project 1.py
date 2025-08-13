import os  # For interacting with the operating system (e.g., file paths, directories)
import webbrowser  # For opening web pages in a browser
import datetime  # For working with dates and times
import pyttsx3  # For text-to-speech conversion
import speech_recognition as sr  # For recognizing speech from microphone input
import pyautogui  # For taking screenshots

# Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')  # Use SAPI5 on Windows for speech synthesis 
voices = engine.getProperty('voices')  # Get available voices
engine.setProperty('voice', voices[0].id)  # Set the voice (0 for male, 1 for female)

def say(text): 
    """Converts text to speech and speaks it aloud"""
    engine.say(text)  # Add text to the speech queue
    engine.runAndWait()  # Wait for the speech to finish

def wishMe():
    """Greets the user based on the current time of day"""
    hour = int(datetime.datetime.now().hour)  # Get the current hour
    if 0 <= hour < 12:
        say("Good Morning!")  # Morning greeting
    elif 12 <= hour < 18:
        say("Good Afternoon!")  # Afternoon greeting
    else:
        say("Good Evening!")  # Evening greeting
    say("I am JARVIS. How can I assist you?")  # Introduction

def takeCommand():
    """Listens to user voice input and converts it to text"""
    r = sr.Recognizer()  # Initialize the recognizer
    with sr.Microphone() as source:  # Use the microphone as the audio source
        print("Listening...")  # Indicate that the program is listening
        r.pause_threshold = 1  # Set pause threshold to 1 second
        r.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = r.listen(source)  # Listen to the user's voice
        try:
            print("Recognizing...")  # Indicate that the program is recognizing speech
            query = r.recognize_google(audio, language="en-in")  # Convert speech to text using Google API
            print(f"User said: {query}")  # Print the recognized text
            return query.lower()  # Return the query in lowercase
        except Exception as e:
            print("Error in speech recognition:", e)  # Print error if recognition fails
            return "Some error occurred. Sorry from Jarvis."  # Return error message

def openOnYouTube(query):
    """Opens the specified query on YouTube"""
    try:
        say(f"Opening {query} on YouTube.")  # Announce the action
        query = query.replace(" ", "+")  # Replace spaces with '+' for the URL
        url = f"https://www.youtube.com/results?search_query={query}"  # Create the YouTube search URL
        webbrowser.open(url)  # Open the URL in the default browser
    except Exception as e:
        print("Error opening YouTube:", e)  # Print error if YouTube fails to open
        say("Sorry, I couldn't open that on YouTube.")  # Speak error message

def searchOnGoogle(query):
    """Searches the specified query on Google"""
    try:
        say(f"Searching {query} on Google.")  # Announce the action
        query = query.replace(" ", "+")  # Replace spaces with '+' for the URL
        url = f"https://www.google.com/search?q={query}"  # Create the Google search URL
        webbrowser.open(url)  # Open the URL in the default browser
    except Exception as e:
        print("Error searching Google:", e)  # Print error if Google search fails
        say("Sorry, I couldn't search that on Google.")  # Speak error message

def takeScreenshot():
    """Takes a screenshot and saves it to the Screenshots folder"""
    try:
        if not os.path.exists("Screenshots"):  # Check if Screenshots folder exists
            os.mkdir("Screenshots")  # Create the folder if it doesn't exist
            print("Screenshots folder created.")  # Debug message
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Generate a timestamp
        screenshot_path = os.path.join("Screenshots", f"screenshot_{timestamp}.png")  # Create file path
        print(f"Screenshot path: {screenshot_path}")  # Debug message
        
        screenshot = pyautogui.screenshot()  # Capture the screenshot
        print("Screenshot captured.")  # Debug message
        screenshot.save(screenshot_path)  # Save the screenshot
        print("Screenshot saved.")  # Debug message
        say("Screenshot taken and saved.")  # Announce the action
    except Exception as e:
        print("Error taking screenshot:", e)  # Print error if screenshot fails
        say("Sorry, I couldn't take a screenshot.")  # Speak error message

if __name__ == '__main__':
    wishMe()  # Greet the user
    while True:
        query = takeCommand()  # Listen for user commands
        
        # Open websites
        sites = [
            ["youtube", "https://www.youtube.com"],  # YouTube URL
            ["wikipedia", "https://www.wikipedia.com"],  # Wikipedia URL
            ["google", "https://www.google.com"],  # Google URL
        ]
        for site in sites:
            if f"open {site[0]}".lower() in query:  # Check if user asked to open a site
                say(f"Opening {site[0]} sir...")  # Announce the action
                webbrowser.open(site[1])  # Open the site in the browser

        # Play music from local folder
        if "play music" in query:  # Check if user asked to play music
            music_dir = r"C:\\Musicc"  # Path to the music folder
            songs = os.listdir(music_dir)  # List all files in the folder
            if songs:  # If there are songs
                os.startfile(os.path.join(music_dir, songs[0]))  # Play the first song
                say("Playing music.")  # Announce the action
            else:
                say("No music files found in the folder.")  # Speak error message

        # Open something on YouTube
        elif "open" in query and "on youtube" in query:  # Check if user asked to open something on YouTube
            search_query = query.replace("open", "").replace("on youtube", "").strip()  # Extract the search query
            if search_query:  # If query is not empty
                openOnYouTube(search_query)  # Open the query on YouTube
            else:
                say("Please specify what to open on YouTube.")  # Speak error message

        # Search something on Google
        elif "search" in query and "on google" in query:  # Check if user asked to search on Google
            search_query = query.replace("search", "").replace("on google", "").strip()  # Extract the search query
            if search_query:  # If query is not empty
                searchOnGoogle(search_query)  # Search the query on Google
            else:
                say("Please specify what to search on Google.")  # Speak error message

        # Take a screenshot
        elif "take screenshot" in query or "screenshot" in query:  # Check if user asked to take a screenshot
            say("Taking a screenshot.")  # Announce the action
            takeScreenshot()  # Take the screenshot

        # Tell the time
        elif "the time" in query or "time" in query:  # Check if user asked for the time
            time_str = datetime.datetime.now().strftime("%H:%M:%S")  # Get the current time
            say(f"Sir, the time is {time_str}")  # Speak the time

        # Quit the program
        elif "exit" in query or "quit" in query:  # Check if user asked to exit
            say("Goodbye! Have a great day!")  # Say goodbye
            break  # Exit the loop

        # Default: No matching command
        else:
            say("I'm sorry, I don't understand that command.")  # Speak error message
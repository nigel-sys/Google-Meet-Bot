import time
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pydub import AudioSegment
from pydub.effects import normalize, high_pass_filter
import os
from dotenv import load_dotenv, dotenv_values


class GoogleMeetBot:
    def __init__(self, email, password, meeting_url, output_filename='meeting_audio.wav'):
        self.email = email
        self.password = password
        self.meeting_url = meeting_url
        self.output_filename = output_filename
        self.driver = None

    def initialize_browser(self):
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_argument('--start-maximized')
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(options=opt)

    def login_to_google(self):
        self.driver.get(
            'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')

        self.driver.find_element(By.ID, "identifierId").send_keys(self.email)
        self.driver.find_element(By.ID, "identifierNext").click()
        self.driver.implicitly_wait(10)

        self.driver.find_element(
            By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.ID, "passwordNext").click()
        self.driver.implicitly_wait(10)

        # Wait until Google Home Page is fully loaded
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@aria-label,"Google Account")]')))
            print("Logged in successfully.")
        except TimeoutException:
            print("Login failed. Retrying...")
            self.login_to_google()

    def turn_off_mic_cam(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(@aria-label,"Turn off microphone")]'))).click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(@aria-label,"Turn off camera")]'))).click()

    def join_meeting(self):
        try:
            # Attempt to find and click the "Join now" button
            join_now_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//span[text()="Join now"]/..'))
            )
            join_now_button.click()
            print("Clicked 'Join now'")
        except TimeoutException:
            print(
                "Could not find 'Join now' button. Trying to find 'Ask to join' button...")
        try:
            # If "Join now" is not found, look for the "Ask to join" button
            ask_to_join_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//span[text()="Ask to join"]/..'))
            )
            ask_to_join_button.click()
            print("Clicked 'Ask to join'")
        except TimeoutException:
            print(
                "Could not find 'Ask to join' button. The meeting might not be accessible.")
            self.handle_name_prompt()  # Attempt to handle name prompt, the last case

    def handle_name_prompt(self):
        try:
            name_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//input[@placeholder="Your name"]')))
            name_input.send_keys("Automated User")
            self.driver.find_element(
                By.XPATH, '//span[text()="Join now"]/..').click()
        except TimeoutException:
            print("No name prompt found, there might be another issue.")

    def record_audio(self):
        fs = 44100  # Sample rate
        duration = 1  # Duration of each recording chunk in seconds
        print("Recording...")
        recording = []  # List to store audio chunks

        try:
            while self.is_meeting_running():
                data = sd.rec(int(duration * fs), samplerate=fs,
                              channels=2, dtype='int16')
                sd.wait()
                recording.append(data)
        except KeyboardInterrupt:
            print("Recording stopped manually")

        recording = np.concatenate(recording, axis=0)
        write(self.output_filename, fs, recording)
        print(f"Recording saved as {self.output_filename}")

        # Post-process the recorded audio
        self.post_process_audio()

    def post_process_audio(self):
        print("Post-processing audio...")
        audio = AudioSegment.from_wav(self.output_filename)

        # Normalize the audio to make it louder
        normalized_audio = normalize(audio)

        # Apply a high-pass filter to remove low-frequency noise
        filtered_audio = high_pass_filter(normalized_audio, cutoff=100)

        # Increase the gain by 5dB
        louder_audio = filtered_audio + 5

        # Export the processed audio
        louder_audio.export(self.output_filename, format="wav")
        print(f"Processed audio saved as {self.output_filename}")

    def is_meeting_running(self):
        try:
            self.driver.find_element(By.XPATH, '//*[contains(text(),"You")]')
            return True
        except:
            return False

    def start(self):
        self.initialize_browser()
        self.login_to_google()
        self.driver.get(self.meeting_url)
        self.turn_off_mic_cam()
        self.join_meeting()

        recording_thread = threading.Thread(target=self.record_audio)
        recording_thread.start()

        try:
            while self.is_meeting_running():
                time.sleep(10)
        except KeyboardInterrupt:
            print("Bot stopped manually")

        self.driver.quit()


# Usage
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
meeting_url = input("Please enter the Google Meet link: ")
bot = GoogleMeetBot(email, password, meeting_url)
bot.start()

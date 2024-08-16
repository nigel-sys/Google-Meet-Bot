# Google Meet Bot

This Python-based bot automates the process of joining Google Meet meetings, turning off the microphone and camera, and recording audio from the meeting. It uses `Selenium` for browser automation and `sounddevice` for audio recording. The recorded audio is post-processed to improve quality.

## Features

- **Automated Google Account Login:** Logs into a Google account using provided credentials.
- **Meeting Automation:** Joins a Google Meet meeting by finding and clicking the appropriate buttons.
- **Audio Recording:** Records meeting audio, saves it as a `.wav` file, and applies audio processing to enhance quality.
- **Post-Processing:** Normalizes the audio and applies a high-pass filter to improve clarity.

## Requirements

- Python 3.x
- Google Chrome
- ChromeDriver
- Required Python libraries (listed in `requirements.txt`)

## Installation

1. **Clone the Repository:**

   `git clone https://github.com/nigel-sys/Google-Meet-Bot.git`

   `cd Google-Meet-Bot`

2. **Set Up a Virtual Environment (Recommended):**

   `python -m venv venv`

   `source venv/bin/activate` _(On Windows use `venv\Scripts\activate`)_

3. **Install Dependencies:**

   `pip install -r requirements.txt`

4. **Create a `.env` File:**

   Create a `.env` file in the root directory of the project and add your Google account credentials:

   EMAIL=your-email@example.com
   PASSWORD=your-password

## Usage

1. **Run the Bot:**

`python google_meet_bot.py`

2. **Input the Google Meet Link:**

When prompted, enter the Google Meet link of the meeting you want to join.

## Configuration

- **Email and Password:** Set your Google account credentials in the `.env` file.
- **Meeting URL:** Provide the Google Meet URL when prompted by the script.
- **Output File:** The recorded audio is saved as `meeting_audio.wav` by default. You can change the filename in the `GoogleMeetBot` class constructor.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Selenium for browser automation
- `sounddevice` and `pydub` for audio processing

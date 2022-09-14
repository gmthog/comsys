DOORBELL_PIN = 26
DOORBELL_SCREEN_ACTIVE_S = 60
# Path to the SFX file
RING_SFX_PATH = None  # If None, no sound effect plays
# RING_SFX_PATH = "/home/pi/ring.wav"
SENDER_EMAIL = 'senderr999@gmail.com'
SENDER_PASSWORD = 'qlehnifbbnixrivf'
SENDER_EMAIL = 'phamminhhoang317@gmail.com'
RING_SFX_PATH = Doorbell-SoundBible.com-516741062.mp3


import time
import os
import signal
import subprocess
import smtplib
import uuid
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import RPi.GPIO as GPIO

# try:
# except RuntimeError:
#     print("Error importing RPi.GPIO. This is probably because you need superuser. Try running again with 'sudo'.")


# def show_screen():
#     os.system("tvservice -p")
#     os.system("xset dpms force on")


# def hide_screen():
#     os.system("tvservice -o")


def send_email_notification(chat_url):
    sender = EmailSender(SENDER_EMAIL, SENDER_PASSWORD)
    email = Email(
        sender,
        'Video Doorbell',
        'Notification: A visitor is waiting',
        'A video doorbell caller is waiting on the virtual meeting room. Meet them at %s' % chat_url
    )
    email.send(SENDER_EMAIL)


def ring_doorbell(pin):
    SoundEffect(RING_SFX_PATH).play()

    chat_id = str(uuid.uuid4())
    video_chat = VideoChat(chat_id)
    send_email_notification(video_chat.get_chat_url())
   
    # show_screen()

    video_chat.start()
    time.sleep(DOORBELL_SCREEN_ACTIVE_S)
    video_chat.end()

    # hide_screen()


class SoundEffect:
    def __init__(self, filepath):
        self.filepath = filepath

    def play(self):
        if self.filepath:
            subprocess.Popen(["aplay", self.filepath])


class VideoChat:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self._process = None

    def get_chat_url(self):
        return "http://meet.jit.si/%s#config.prejoinPageEnabled=false" % self.chat_id

    def start(self):
        if not self._process and self.chat_id:
            self._process = subprocess.Popen(["chromium-browser", "-kiosk", self.get_chat_url()])
        else:
            print("Can't start video chat")

    def end(self):
        if self._process:
            os.kill(self._process.pid, signal.SIGTERM)


class EmailSender:
    def __init__(self, email, password):
        self.email = email
        self.password = password


class Email:
    def __init__(self, sender, subject, preamble, body):
        self.sender = sender
        self.subject = subject
        self.preamble = preamble
        self.body = body

    def send(self, sender_email):
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.subject
        msgRoot['From'] = self.sender.email
        msgRoot['To'] = sender_email
        msgRoot.preamble = self.preamble

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText(self.body)
        msgAlternative.attach(msgText)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(self.sender.email, self.sender.password)
        smtp.sendmail(self.sender.email, sender_email, msgRoot.as_string())
        smtp.quit()


class Doorbell:
    def __init__(self, doorbell_button_pin):
        self._doorbell_button_pin = doorbell_button_pin

    def run(self):
        try:
            print("Starting Doorbell...")
            # hide_screen()
            self._setup_gpio()
            print("Waiting for doorbell rings...")
            self._wait_forever()

        except KeyboardInterrupt:
            print("Safely shutting down...")

        finally:
            self._cleanup()

    def _wait_forever(self):
        while True:
            time.sleep(0.1)

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._doorbell_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self._doorbell_button_pin, GPIO.RISING, callback=ring_doorbell, bouncetime=2000)

    def _cleanup(self):
        GPIO.cleanup(self._doorbell_button_pin)
        show_screen()


if __name__ == "__main__":
    doorbell = Doorbell(DOORBELL_PIN)
    doorbell.run()

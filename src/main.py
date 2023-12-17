# Copyright (C) 2022 Hemant Sachdeva <hemant.evolver@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys

import requests

from src.life import about_me, contributions, educations, experiences, gallery

try:
    from flask import Flask, render_template, request
except ImportError:
    sys.exit("[!] Flask module not found. Install it by 'pip3 install flask'")

application = Flask(__name__)

RECAPTCHA_SITE_KEY = os.getenv("SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("SECRET_KEY")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def bot_message(data):
    # Get the bot API key from the environment variable
    BOT_API = os.getenv("BOT_API")
    # Get the chat ID from the environment variable
    CHAT_ID = os.getenv("CHAT_ID")
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    # Check if the sender or the message is in blacklist
    fields = {
        name,
        email,
        subject,
        message
    }

    TEXT_MESSAGE = f"Name: <code>{name}</code>\nEmail: <code>{email}</code>\nSubject: <code>{subject}</code>\nMessage: <code>{message}</code>"
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": TEXT_MESSAGE,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


@application.route('/')
def index():
    context = {
        'about': about_me,
        'contributions': contributions,
        'educations': educations,
        'experiences': experiences,
        'gallery': gallery
    }
    return render_template('index.html', context=context, site_key=RECAPTCHA_SITE_KEY)


@application.route('/send_message', methods=['POST'])
def send_message():
    data = request.form.to_dict()

    recaptcha_secret_response = request.form['g-recaptcha-response']

    verify_response = requests.post(
        url=f'{RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_SECRET_KEY}&response={recaptcha_secret_response}').json()

    if verify_response['success'] == False or verify_response['score'] < 0.5:
        return
    bot_message(data)
    return render_template('index.html', context=None)

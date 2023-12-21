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
    from flask_wtf import FlaskForm
    from wtforms import StringField, TextAreaField
    from wtforms.validators import DataRequired, Email
except ImportError:
    sys.exit("[!] Flask module not found. Install it by 'pip3 install flask'")

application = Flask(__name__)
application.secret_key = os.getenv("APP_SECRET_KEY")

RECAPTCHA_SITE_KEY = os.getenv("SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("SECRET_KEY")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()], render_kw={
        'style': 'color: white;'})
    email = StringField('Your Email', validators=[DataRequired(), Email()], render_kw={
        'style': 'color: white;'})
    subject = StringField('Subject', validators=[DataRequired()], render_kw={
        'style': 'color: white;'})
    message = TextAreaField('Message', validators=[DataRequired()], render_kw={
                            'style': 'color: white;'})


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


context = {
    'about': about_me,
    'contributions': contributions,
    'educations': educations,
    'experiences': experiences,
    'gallery': gallery
}


@application.route('/')
def index():
    return render_template('index.html', context=context, site_key=RECAPTCHA_SITE_KEY, form=ContactForm())


@application.route('/send_message', methods=['POST'])
def send_message():
    form = ContactForm(request.form)

    if form.validate_on_submit():
        # Form data is valid, process it
        recaptcha_secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(
            url=f'{RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_SECRET_KEY}&response={recaptcha_secret_response}').json()

        if verify_response['success'] == False or verify_response['score'] < 0.5:
            return render_template('index.html', context=context, site_key=RECAPTCHA_SITE_KEY, message="Recaptcha verification failed", form=form)

        bot_message(form.data)
        return render_template('index.html', context=context, site_key=RECAPTCHA_SITE_KEY, message="Message sent successfully", form=ContactForm())

    else:
        # Form data is invalid
        return render_template('index.html', context=context, site_key=RECAPTCHA_SITE_KEY, message="Failed form validation", form=form)

    recaptcha_secret_response = request.form['g-recaptcha-response']

    verify_response = requests.post(
        url=f'{RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_SECRET_KEY}&response={recaptcha_secret_response}').json()

    if verify_response['success'] == False or verify_response['score'] < 0.5:
        return render_template('index.html', message="Failed reCAPTCHA verification", site_key=RECAPTCHA_SITE_KEY, context=context)
    bot_message(data)
    return render_template('index.html', message="Message sent successfully", site_key=RECAPTCHA_SITE_KEY, context=context)

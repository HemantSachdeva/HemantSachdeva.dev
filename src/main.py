# Copyright (C) 2021 Hemant Sachdeva <hemant.evolver@gmail.com>

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

import sys

try:
    from flask import Flask, redirect, render_template, request
except ImportError:
    sys.exit("[!] Flask module not found. Install it by 'pip3 install flask'")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def write_to_file(data):
    with open('submits.csv', mode='a') as database:
        email = data.get("email")
        subject = data.get("subject")
        message = data.get("message")
        database.write(f'\n{email},{subject},{message}')


@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        data = request.form.to_dict()
        write_to_file(data)
        return render_template('/thankyou.html')
    else:
        return render_template('/error.html')

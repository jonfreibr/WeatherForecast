#!/usr/bin/env python3
"""
Program : Weather Forecast
Author  : Jon Freivald <jfreivald@brmedical.com>
        : Copyright © Blue Ridge Medical Center, 2025. All Rights Reserved
        : License: GNU GPL Version 3
Date    : 2025-07-21
Purpose : To poll the National Weather Service for location specific forecasts
        : Version change log at EoF.
"""

import atexit
import json
import os
import psutil
import requests
import subprocess
import sys

from datetime import datetime

from PySide6.QtGui import (
    QIcon,
)

from PySide6 import (
    QtCore,
)

from PySide6.QtCore import (
    QTimer,
    QSettings,
    QPoint,
    QSize,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QDialog,
    QTextEdit,
    QApplication,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QDialogButtonBox,
)

progver = '0.1'

brmc_dark_blue = '#00446a'
brmc_medium_blue = '#73afb6'
brmc_gold = '#ffcf01'
brmc_rust = '#ce7067'
brmc_warm_grey = '#9a8b7d'

#--------------------------------------------------------------------------------------------------------------------------------

# Configuration Information

num_cols = 10
loc_config = 'forecast.json' # If you change this, update your update_script!
default_locations = {"BRMC Arrington":"37.7066,-78.9340",
                     "BRMC Amherst":"37.5655,-79.0637",
                     "BRMC Appomattox":"37.3673,-78.8267"}
update_source = 'H:/_BRMCApps/WeatherForecast/forecast.py'
update_script = 'H:/_BRMCApps/WeatherForecast/install.bat'

#--------------------------------------------------------------------------------------------------------------------------------

try:
    with open(loc_config, "r") as file:
        locations = json.load(file)
except:
    locations = default_locations
    
buttons = []

#--------------------------------------------------------------------------------------------------------------------------------

class UpdateDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        self.setWindowTitle("Update Available!")
        layout = QVBoxLayout()
        self.label = QLabel("There is an update available for the Weather Alert application.")
        self.label2 = QLabel("Automatic updates are only available for Windows at this time.")
        self.label3 = QLabel("Other platforms please check with your systems administrator.")
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.label)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)
        layout.addWidget(button_box)
        self.setLayout(layout)

#--------------------------------------------------------------------------------------------------------------------------------

def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid !=os.getpid():
                return True
            
    return False

#--------------------------------------------------------------------------------------------------------------------------------

def update_app():
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", update_script, "/min"], stdout=None, stderr=None)

#--------------------------------------------------------------------------------------------------------------------------------

class Location:

    headers = {
        "User-Agent": "BRMC Weather Forecast App, jfreivald@brmedical.com"
    }

    def __init__(self, name, lat, lon):
        self.lat = lat
        self.lon = lon
        self.name = name
        self.button = QPushButton(self.name)
        self.button.clicked.connect(self.display)
        self.button_normal()
        try:
            self.point_data = requests.get(f'https://api.weather.gov/points/{self.lat},{self.lon}').json()
            self.forecast_url = self.point_data['properties']['forecast']
        except:
            pass

    def update(self):
        try:
            self.response = requests.get(f'{self.forecast_url}')
        except:
            self.response = {'title': 'API Not Available!', 'updated': 'Not updated!', 'Retrieved': 'Not Retrieved'}
        return self.response

    def get_button(self):
        return self.button

    def button_grey(self):
        self.button.setStyleSheet(f'background-color: {brmc_warm_grey}; color: {brmc_gold}')

    def button_normal(self):
        self.button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')

    def button_red(self):
        self.button.setStyleSheet('background-color: red; color: black')

    def display(self):
        self.update()
        self.out = DataWindow(self.response, self.name)
        self.out.show()

#--------------------------------------------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("Blue Ridge Medical Center", "Weather Forecast Widget")
        self.resize(self.settings.value('MainWindowSize', QSize(450, 50)))
        self.move(self.settings.value('MainWindowPos', QPoint(50,50)))

        self.setStyleSheet(f'background-color: {brmc_medium_blue}')

        self.setWindowTitle(f'Weather Widget {progver}')
        container = QWidget()
        layout = QGridLayout()

        for i in locations.keys():
            lat, lon = locations[i].split(',')
            buttons.append(Location(i, lat, lon))

        x = 0
        y = 0
        for j in buttons:
            layout.addWidget(j.get_button(), y, x)
            x += 1
            if x >= num_cols:
                x = 0
                y += 1

        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, a0):
        self.settings.setValue('MainWindowSize', self.size())
        self.settings.setValue('MainWindowPos', self.pos())
        return super().closeEvent(a0)

#--------------------------------------------------------------------------------------------------------------------------------

class DataWindow(QWidget):
    def __init__(self, response, name):
        super().__init__()

        self.response = response.json()
        self.name = name
        self.namePos = name+'pos'
        self.nameSize = name+'size'
        self.setWindowTitle(f'Weather forecast for {self.name}')
        self.setContentsMargins(10, 10, 10, 10)
        self.settings = QSettings("Blue Ridge Medical Center", "Weather Forecast Widget")
        self.resize(self.settings.value(self.nameSize, QSize(655, 600)))
        self.move(self.settings.value(self.namePos, QPoint(50,150)))
        self.setStyleSheet(f'background-color: {brmc_medium_blue}; color: black')
        layout = QHBoxLayout()

        divLine = "\n|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|\n"

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(f'background-color: {brmc_gold}; color: black')

        for period in self.response['properties']['periods']:
            self.text_edit.insertPlainText(str(period['name']+':\n'))
            self.text_edit.insertPlainText(str('Temperature: '+str(period['temperature'])+' '+period['temperatureUnit']+'\n'))
            self.text_edit.insertPlainText(str('Wind: '+str(period['windSpeed'])+' '+period['windDirection']+'\n'))
            self.text_edit.insertPlainText(str('Detailed Forecast: '+period['detailedForecast']+'\n'))
            self.text_edit.insertPlainText(divLine)
        self.text_edit.insertPlainText('End of Forecast')

        self.cursor = self.text_edit.textCursor()
        self.cursor.setPosition(0)
        self.text_edit.setTextCursor(self.cursor)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def closeEvent(self, a0):
        self.settings.setValue(self.nameSize, self.size())
        self.settings.setValue(self.namePos, self.pos())
        return super().closeEvent(a0)

#--------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    if is_running(os.path.basename(__file__)):
        sys.exit()

    app = QApplication(sys.argv)
    if sys.platform == "win32":
        try:
            update = datetime.fromtimestamp(os.path.getmtime(__file__)).strftime("%m/%d/%y @ %H:%M:%S") < datetime.fromtimestamp(os.path.getmtime(update_source)).strftime("%m/%d/%y @ %H:%M:%S")
        except:
            update = False
        if update:
            atexit.register(update_app)
            dialog = UpdateDialog()
            if dialog.exec():
                sys.exit()
            else:
                atexit.unregister(update_app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

#--------------------------------------------------------------------------------------------------------------------------------
"""
Change log:

v 0.1       : 250721        : Initial version
"""
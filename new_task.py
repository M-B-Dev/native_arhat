import json
from datetime import datetime

import requests
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from kivymd.uix.picker import MDDatePicker, MDTimePicker


class NewTask(Screen):
    token = ObjectProperty(None)
    user_id = ObjectProperty(None)
    task_description = ObjectProperty(None)
    start_time = ObjectProperty(None)
    end_time = ObjectProperty(None)
    frequency = ObjectProperty(None)
    start_date = ObjectProperty(None)
    end_date = ObjectProperty(None)
    start_time_minutes = ObjectProperty(None)
    end_time_minutes = ObjectProperty(None)
    updated_tasks = ObjectProperty(None)
    
    
    def get_end_date(self, date):
        '''
        :type date: <class 'datetime.date'>
        '''
        self.end_date.text = datetime.strftime(date, "%d-%m-%Y")

    def get_start_date(self, date):
        '''
        :type date: <class 'datetime.date'>
        '''
        self.start_date.text = datetime.strftime(date, "%d-%m-%Y")

    def show_date_picker(self, mode):
        if mode == "end":
            date_dialog = MDDatePicker(callback=self.get_end_date)
        else:
            date_dialog = MDDatePicker(callback=self.get_start_date)
        date_dialog.open()

    def show_start_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_start_time)
        time_dialog.open()

    def get_start_time(self, instance, time):
        self.start_time.text = str(time)
        self.start_time_minutes = time

    def show_end_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_end_time)
        time_dialog.open()

    def get_end_time(self, instance, time):
        self.end_time.text = str(time)
        self.end_time_minutes = time


    def create_new_task(self):
        if self.end_time_minutes and self.start_time_minutes and self.start_date:
            self.end_time_minutes = (self.end_time_minutes.hour * 60) + self.end_time_minutes.minute
            self.start_time_minutes = (self.start_time_minutes.hour * 60) + self.start_time_minutes.minute
            if self.frequency.text:
                if self.frequency.text.isnumeric() is True:
                    frequency = int(self.frequency.text)
                else:
                    self.frequency.text = "This must be a number"
                    return None
            else:
                frequency = None
            if self.end_date.text:
                to_date = self.end_date.text
            else:
                to_date = None
            data = {
                'body': self.task_description.text, 
                'start_time': self.start_time_minutes, 
                'end_time': self.end_time_minutes, 
                'frequency': frequency, 
                'date': self.start_date.text, 
                'to_date': to_date,
                'user_id': self.user_id
            }
            hed = {'Authorization': 'Bearer ' + self.token}
            response = requests.post(f'https://arhat.uk/api/tasks/{self.user_id}/{self.start_date.text}', json=data, headers=hed)
            self.task_description.text = ""
            self.start_time.text = ""
            self.end_time.text = ""
            self.frequency.text = ""
            self.start_date.text = ""
            self.end_date.text = ""
            self.start_time_minutes = 0
            self.end_time_minutes = 0
            self.updated_tasks = json.loads(response.content)
            self.manager.current = "Tasks"

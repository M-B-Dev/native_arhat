import json

import requests
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from validate_email import validate_email


class Register(Screen):
    rusername = ObjectProperty(None)
    email = ObjectProperty(None)
    password1 = ObjectProperty(None)
    password2 = ObjectProperty(None)

    def register_new_user(self):
        errors = {}
        if not self.email.text or validate_email(self.email.text) is not True:
            errors['email'] = "Please enter a valid email address."
        if not self.password1.text and not self.password2.text or self.password1.text != self.password2.text:
            errors['password'] = "Please enter matching passwords."
        if errors:
            for error in errors.keys():
                if error == 'email':
                    self.email.helper_text_mode = "persistent"
                    self.email.helper_text = errors['email']
                    self.email.error = True
                if error == 'password':
                    self.password1.helper_text_mode = "persistent"
                    self.password2.helper_text_mode = "persistent"
                    self.password1.error = True
                    self.password2.error = True
                    self.password1.helper_text = errors['password']
                    self.password2.helper_text = errors['password']
            return False
        data = {
            'username': self.rusername.text,
            'email': self.email.text,
            'password': self.password1.text
        }
        response = requests.post('https://arhat.uk/api/users', json=data)
        if 'error' in json.loads(response.content):
            if 'username' in json.loads(response.content)['message']:
                self.rusername.helper_text_mode = "persistent"
                self.rusername.helper_text = json.loads(response.content)['message']
                self.rusername.error = True
            if 'email' in json.loads(response.content)['message']:
                self.email.helper_text_mode = "persistent"
                self.email.error = True
                self.email.helper_text = json.loads(response.content)['email']
            return False
        return True

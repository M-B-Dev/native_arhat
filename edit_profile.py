import json

import requests
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from kivymd.uix.textfield import MDTextField
from validate_email import validate_email


class EditProfile(Screen):
    user = ObjectProperty(None)
    internal_password = ObjectProperty(None)
    token = ObjectProperty(None)

    def set_text_fields(self):
        number_of_widgets = len(self.children[0].children[1].children)
        for i in range(number_of_widgets):
            self.children[0].children[1].remove_widget(self.children[0].children[1].children[0])
        self.field_names = {
            'username': self.user['username'],
            'email': self.user['email'],
            'password1': self.internal_password,
            'password2': self.internal_password,
            'days': str(self.user['days']),
            'threshold': str(self.user['threshold']) 
        }
        y = 0.9
        for field in self.field_names.keys():
            if 'password' in field:
                password = True
            else:
                password = False
            setattr(self, field, MDTextField(
                write_tab=False,
                id=field,
                text=self.field_names[field],
                required=True,
                mode="rectangle",
                pos_hint={"center_x": 0.5, "center_y": y},
                password=password
            ))
            y - 0.2
            widget = getattr(self, field)
            self.children[0].children[1].add_widget(widget)
        self.edit_profile_button = MDRaisedButton(text="Edit Profile", pos_hint={"center_x": 0.5, "center_y": 0})
        self.edit_profile_button.bind(on_release=self.edit_profile)
        self.children[0].children[1].add_widget(self.edit_profile_button)
        
            

    def edit_profile(self, instance):
        errors = False
        if self.password1.text != self.password2.text or len(self.password1.text) < 8:
            self.password1.helper_text = "Please enter identical passwords of 8 characters or more."
            self.password2.helper_text = "Please enter identical passwords of 8 characters or more."
            self.password1.helper_text_mode = "persistent"
            self.password2.helper_text_mode = "persistent"
            errors = True
        if not self.email.text or validate_email(self.email.text) is False:
            self.email.helper_text = "Please enter a valid email address"
            self.email.helper_text_mode = "persistent"
            errors = True
        if not self.threshold.text or self.threshold.text.isnumeric() is False or int(self.threshold.text) > 100:
            self.threshold.helper_text = "Please enter a number between 0 and 100"
            self.threshold.helper_text_mode = "persistent"
            errors = True
        if not self.days.text or self.days.text.isnumeric() is False:
            self.days.helper_text = "Please enter a number"
            self.days.helper_text_mode = "persistent"
            errors = True
        if errors is True:
            return False
        hed = {'Authorization': 'Bearer ' + self.token}
        data = {
            'username': self.username.text,
            'email': self.email.text,
            'threshold': int(self.threshold.text),
            'days': int(self.days.text),
            'password': self.password1.text
            }
        response = requests.put(f'https://arhat.uk/api/users/{self.user["id"]}', json=data, headers=hed)
        if 'error' in json.loads(response.content):
            if 'username' in json.loads(response.content)['error']:
                self.username.helper_text = "That username is taken" 
                self.username.helper_text_mode = "persistent"
            if 'email' in json.loads(response.content)['error']:
                self.email.helper_text = "That email is already registered" 
                self.email.helper_text_mode = "persistent"
            return False
        self.update_fields()

    def update_fields(self):
        hed = {'Authorization': 'Bearer ' + self.token}
        self.user = json.loads(requests.get(f'https://arhat.uk/api/users/{self.user["id"]}', headers=hed).content)
        self.set_text_fields()

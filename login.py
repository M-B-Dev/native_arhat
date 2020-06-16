import json

import requests
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from requests.auth import HTTPBasicAuth


class Login(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    token = ObjectProperty(None)
    user_id = ObjectProperty(None)
    user = ObjectProperty(None)
    internal_password = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Login, self).__init__(**kwargs)
        self.token = ''

    def login_user(self):
        if self.username.text and self.password.text:
            response = requests.post('https://arhat.uk/api/tokens', auth=HTTPBasicAuth(self.username.text, self.password.text))
            if 'token' in json.loads(response.content):
                self.token = json.loads(response.content)['token']
                self.user_id = json.loads(response.content)['id']
                self.manager.current = "Tasks"
            else:
                return None
            self.internal_password = self.password.text
            self.username.text = ''
            self.password.text = ''
            hed = {'Authorization': 'Bearer ' + self.token}
            self.user = json.loads(requests.get(f'https://arhat.uk/api/users/{self.user_id}', headers=hed).content)
            return self.token


from datetime import datetime

import asynckivy
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from plyer import notification, vibrator

from contacts import Contacts
from edit_profile import EditProfile
from login import Login
from messages import Messages
from nav_drawer import ContentNavigationDrawer, List
from new_task import NewTask
from register import Register
from tasks import Tasks


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Arhat"
        self.theme_cls.primary_palette = "BlueGray"
        super().__init__(**kwargs)

    def build(self):
        return Builder.load_file("arhat.kv")
    
    def on_call(self, tasks):
        async def notify_tasks(tasks):
            sleep = asynckivy.sleep
            now = (datetime.utcnow().hour * 60) + datetime.utcnow().minute
            for task in tasks:
                if int(task['end_time']) > now:
                    await sleep((int(task['end_time']) - now)*60)
                    notification.notify("Have you done this task:", task['body'])
                    vibrator.vibrate(time=2)
        asynckivy.start(notify_tasks(tasks))

if __name__ == "__main__":
    MainApp().run()

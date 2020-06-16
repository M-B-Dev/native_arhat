from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)


class ContentNavigationDrawer(BoxLayout):
    window_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class ButtonTemplate(OneLineIconListItem):
    pass

class List(MDList):
    def __init__(self, **kwargs):
        super(List, self).__init__(**kwargs)
        self.nav_buttons = {
            'Tasks': "calendar-multiple-check",
            'New Task': "calendar-check",
            'Messages': "message-text-outline",
            'Contacts': "account-network",
            'Edit Profile': "account-circle-outline",
            'Logout': "logout",
            'Login': "account-circle",
            'Register': "account-plus"
        }
        self.logged_out_buttons()

    def logged_out_buttons(self):
        self.remove_buttons()
        for button_name in self.nav_buttons.keys():
            if button_name == 'Login' or button_name == 'Register':
                button = ButtonTemplate()
                button.text = button_name
                button.icon = self.nav_buttons[button_name]
                button.id = button_name
                button.add_widget(IconLeftWidget(id=button.icon, icon=button.icon))
                self.add_widget(button)

    def remove_buttons(self):
        number_of_kids = range(len(self.children))
        for i in number_of_kids:
            self.remove_widget(self.children[0])

    def logged_in_buttons(self):
        self.remove_buttons()
        for button_name in self.nav_buttons.keys():
            if button_name != 'Login' and button_name != 'Register':
                button = ButtonTemplate()
                button.text = button_name
                button.icon = self.nav_buttons[button_name]
                button.id = button_name
                button.add_widget(IconLeftWidget(id=button.icon, icon=button.icon))
                self.add_widget(button)  

import json

import requests
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from kivymd.uix.textfield import MDTextField


class MessageScrollView(ScrollView):
    def on_scroll_move(self, touch):
        if self.scroll_y < 0:
            self.add_widges(self)
        return super(MessageScrollView, self).on_scroll_move(touch)
    
    def add_widges(self, touch):
        layout = self.children[0]
        layout_childrens = len(layout.children)
        message_type = self.parent.parent.message_type
        if self.parent.parent.message_type == "received":
            id_type = "sender_id"
        else:
            id_type = "recipient_id" 
        if len(self.parent.parent.messages) > 0:
            msg = self.parent.parent.messages[0]
            inner_widg = Button()
            inner_widg.pos_hint = {'x': 0, 'y': 0.5}
            inner_widg.bg_color = (0,0,0,0.25)
            inner_widg.size_hint_y = None
            inner_widg.height = 50
            for user in self.parent.parent.idents:
                if user['id'] == msg[id_type]:
                    if message_type == "received":
                        inner_widg.text = f'{user["username"]} sent you a message on {msg["timestamp"]}'
                    else:
                        inner_widg.text = f'You sent a message to {user["username"]} on {msg["timestamp"]}'   
                    msg[f'{message_type}'] = user["username"]
            inner_widg.id = json.dumps(msg)
            inner_widg.bind(on_release=self.parent.parent.show_message)
            layout.add_widget(inner_widg)
            self.parent.parent.messages.remove(msg)
            bar_position = layout_childrens / (layout_childrens + len(self.parent.parent.messages))
            self.scroll_y = 100 - 100 * bar_position
            self.effect_y.value = self.effect_y.min - self.effect_y.min * bar_position


class Messages(Screen):
    user = ObjectProperty(None)
    token = ObjectProperty(None)
    user_id = ObjectProperty(None)
    body = ObjectProperty(None)
    messages = ObjectProperty(None)

    def show_messages(self, message_type="received"):
        self.message_type = message_type
        number_of_widgets = len(self.children[0].children[0].children[0].children)
        for i in range(number_of_widgets):
            self.children[0].children[0].children[0].remove_widget(self.children[0].children[0].children[0].children[0])
        if message_type == "received":
            button_text = "sent"
            id_type = "sender_id"
        else:
            button_text = "received" 
            id_type = "recipient_id"  
        self.button = MDRaisedButton(text=button_text, pos_hint={'x': 0, 'y': 0.5})
        self.button.id = button_text
        self.button.bind(on_release=self.display_correct_messages)
        self.children[0].children[0].children[0].add_widget(self.button)
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.get(f'https://arhat.uk/api/messages/{message_type}/{self.user_id}', headers=hed)
        self.messages = json.loads(response.content)['items']
        ids = ''
        for id in self.messages:
            ids += f'A{id[id_type]}'
        response = requests.get(f'https://arhat.uk/api/users/{ids}', headers=hed)
        self.idents = json.loads(response.content)
        for i, msg in enumerate(self.messages):
            if i == 20:
                break
            inner_widg = Button()
            inner_widg.size_hint_y = None
            inner_widg.height = 50
            inner_widg.pos_hint = {'x': 0, 'y': 0.5}
            inner_widg.bg_color = (0,0,0,0.25)
            inner_widg.font_size = 10
            for user in self.idents:
                if user['id'] == msg[id_type]:
                    if message_type == "received":
                        inner_widg.text = f'{user["username"]} sent you a message on {msg["timestamp"]}'
                    else:
                        inner_widg.text = f'You sent a message to {user["username"]} on {msg["timestamp"]}'   
                    msg[f'{message_type}'] = user["username"]
            inner_widg.id = json.dumps(msg)
            inner_widg.bind(on_release=self.show_message)
            self.children[0].children[0].children[0].add_widget(inner_widg)
        number_of_messages = len(self.messages)
        for i in range(number_of_messages):
            if i < 20:
                self.messages.remove(self.messages[0])
            else:
                break

    def display_correct_messages(self, instance):
        self.show_messages(message_type=instance.id)

    def show_message(self, instance):
        msg = json.loads(instance.id)
        if 'received' in msg:
            interlocutor = msg['received']
            title = f'Message from {interlocutor}'
            label_text = f'{interlocutor} wrote: {msg["body"]}'
            button_id = str(msg['sender_id'])
        else:
            interlocutor = msg['sent']
            title = f'You sent this to {interlocutor}'
            label_text = f'You wrote: {msg["body"]}'
            button_id = str(msg['recipient_id'])
        layout = BoxLayout()
        layout.orientation = 'vertical'
        body = MDLabel(text=label_text)
        sent_date = MDLabel(text=f'On {msg["timestamp"]}')
        reply_button = Button(text=f'Reply to {interlocutor}')
        reply_button.size_hint_y = None
        reply_button.height = 50
        reply_button.id = button_id
        reply_button.bind(on_release=self.create_message, on_press=self.close_message_dialog)
        layout.add_widget(body)
        layout.add_widget(sent_date)
        layout.add_widget(reply_button)        
        layout.height = layout.minimum_height
        scroller = ScrollView()
        scroller.height = 300
        scroller.add_widget(layout)
        self.msg_dialog = MDDialog(
                auto_dismiss=False,
                title=title,
                type="custom",
                content_cls=scroller,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_press=self.close_message_dialog
                    )
                ],
            )
        self.msg_dialog.open()

    def close_message_dialog(self, instance):
        self.msg_dialog.dismiss()

    def create_message(self, instance):
        layout = BoxLayout()
        layout.orientation = 'vertical'
        for user in self.idents:
            if int(user['id']) == int(instance.id):
                title = f"reply to {user['username']}"
                break
        self.body = MDTextField(hint_text="Type your message here", multiline=True)
        send_button = Button(text='Send Message')
        send_button.size_hint_y = None
        send_button.height = 50
        send_button.bind(on_release=self.send_message, on_press=self.close_send_dialog)
        self.recipient = instance.id
        layout.add_widget(self.body)
        layout.add_widget(send_button)
        scroller = ScrollView()
        scroller.height = 300
        scroller.add_widget(layout)
        self.send_dialog = MDDialog(
                auto_dismiss=False,
                title=title,
                type="custom",
                content_cls=scroller,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_press=self.close_send_dialog
                    )
                ],
            )
        self.send_dialog.open()

    def close_send_dialog(self, instance):
        self.send_dialog.dismiss()

    def send_message(self, instance):
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.post(f'https://arhat.uk/api/users/send/{self.recipient}/{self.user_id}/{self.body.text}', headers=hed)
        print(json.loads(response.content))
        if json.loads(response.content) == 'success':
            self.show_messages(message_type="sent")

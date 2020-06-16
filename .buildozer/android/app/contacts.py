import io
import json

import pybase64 as base64
import requests
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from kivymd.uix.textfield import MDTextField


class Item(OneLineAvatarListItem):
    divider = None
    texture = ObjectProperty(None)


class ContactScrollView(ScrollView):
    def on_scroll_move(self, touch):
        if self.scroll_y < 0:
            self.add_widges(self)
        return super(ContactScrollView, self).on_scroll_move(touch)
    
    def add_widges(self, touch):
        layout = self.children[0]
        layout_childrens = len(layout.children)
        contacts = self.parent.parent
        users = contacts.users
        if len(users) > 0:
            usr = users[0]
            img = base64.b64decode(usr['image'])
            data = io.BytesIO(img)
            fn = f"{usr['username']}.jpg"
            im = CoreImage(data, ext="jpg").texture
            inner_widg = Item(
                pos_hint={'x': 0, 'y': 0},
                bg_color=(0,0,0,0.25),
                id=json.dumps(usr),
                texture=im
            )
            if usr['id'] in contacts.followers_ids and usr['id'] not in contacts.followed_ids:
                inner_widg.text = f"{usr['username']} follows you"
            elif usr['id'] in contacts.followed_ids:
                inner_widg.text = f"You follow {usr['username']}"
            elif usr['id'] in contacts.pender_ids:
                inner_widg.text = f"Pending {usr['username']}"
            elif int(usr['id']) != int(contacts.user_id):
                inner_widg.text = f"Follow {usr['username']}"
            if inner_widg.text:
                inner_widg.bind(on_release=contacts.show_user)
                layout.add_widget(inner_widg)
            contacts.users.remove(usr)
            bar_position = layout_childrens / (layout_childrens + len(contacts.users))
            self.scroll_y = 100 - 100 * bar_position
            self.effect_y.value = self.effect_y.min - self.effect_y.min * bar_position


class Contacts(Screen):
    user = ObjectProperty(None)
    token = ObjectProperty(None)
    user_id = ObjectProperty(None)
    search = ObjectProperty(None)

    def search_users(self, instance):
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.get('https://arhat.uk/api/users', headers=hed)
        self.users = json.loads(response.content)['items']
        users = [user for user in self.users if self.search.text in user['username'] or self.search.text in user['email']]
        if len(self.search.text) > 0:
            search_button_text = "Reset"
        else:
            search_button_text = "    Search    "
        self.show_users(users=users, search_button_text=search_button_text)
        
    def show_users(self, users=None, search_button_text="    Search    "):
        contact_scroll = self.children[0].children[0].children[0]
        number_of_widgets = len(contact_scroll.children)
        for i in range(number_of_widgets):
            contact_scroll.remove_widget(contact_scroll.children[0])
        self.search = MDTextField(
            id='search', 
            pos_hint={'x': 0, 'y': 0.62},
            size_hint_x=None,
            width=self.parent.width / 2
            )
        self.button = MDRectangleFlatIconButton(
            id='btn',
            icon='account-search', 
            pos_hint={'x': 0, 'y': 0.75},
            text=search_button_text
            )
        self.button.bind(on_release=self.search_users)
        contact_scroll.add_widget(self.search)
        contact_scroll.add_widget(self.button)
        self.followers_button = MDRectangleFlatIconButton(text="Followers", icon='account-multiple', pos_hint={'x': 0, 'y': 0.15}, width=self.parent.width / 2, id='flwr_btn')
        self.followers_button.bind(on_release=self.show_followers)
        self.followed_button = MDRectangleFlatIconButton(text="Followed by me", icon='account-multiple-outline', width=self.parent.width / 2, id='flwd_btn', pos_hint={'x': 0, 'y': 0.15})
        self.followed_button.bind(on_release=self.show_followed)
        contact_scroll.add_widget(self.followers_button)
        contact_scroll.add_widget(self.followed_button)
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.get('https://arhat.uk/api/users', headers=hed)
        if not users:
            self.users = json.loads(response.content)['items']
        else:
            self.users = users
        response = requests.get(f'https://arhat.uk/api/users/{self.user_id}/followers', headers=hed)
        self.followers = json.loads(response.content)
        self.followers_ids = [ident['id'] for ident in self.followers['items']]
        response = requests.get(f'https://arhat.uk/api/users/{self.user_id}/followed', headers=hed)
        self.followed = json.loads(response.content)
        self.followed_ids = [ident['id'] for ident in self.followed['items']]
        response = requests.get(f'https://arhat.uk/api/users/{self.user_id}/penders', headers=hed)
        self.penders = json.loads(response.content)
        self.pender_ids = [ident['id'] for ident in self.penders['items']]

        for i, usr in enumerate(self.users):
            if i == 10:
                break
            img = base64.b64decode(usr['image'])
            data = io.BytesIO(img)
            fn = f"{usr['username']}.jpg"
            im = CoreImage(data, ext="jpg").texture
            inner_widg = Item()
            inner_widg.pos_hint = {'x': 0, 'y': 0}
            inner_widg.bg_color = (0,0,0,0.25)
            inner_widg.id = json.dumps(usr)
            if usr['id'] in self.followers_ids and usr['id'] not in self.followed_ids:
                inner_widg.text = f"{usr['username']} follows you"
                self.add_widg(im, inner_widg)
            elif usr['id'] in self.followed_ids:
                inner_widg.text = f"You follow {usr['username']}"
                self.add_widg(im, inner_widg)
            elif usr['id'] in self.pender_ids:
                inner_widg.text = f"Pending {usr['username']}"
                self.add_widg(im, inner_widg)
            elif int(usr['id']) != int(self.user_id):
                inner_widg.text = f"Follow {usr['username']}"
                self.add_widg(im, inner_widg)
        number_of_users = len(self.users)
        for i in range(number_of_users):
            if i == 10:
                break
            self.users.remove(self.users[0])

    def add_widg(self, im, inner_widg):
        inner_widg.texture = im
        inner_widg.bind(on_release=self.show_user)
        self.children[0].children[0].children[0].add_widget(inner_widg)
       
    def follow_user(self, instance):
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.post(f'https://arhat.uk/api/follow/{instance.id}/{self.user_id}', headers=hed)
        self.show_users()

    def unfollow_user(self, instance):
        hed = {'Authorization': 'Bearer ' + self.token}
        response = requests.post(f'https://arhat.uk/api/unfollow/{instance.id}/{self.user_id}', headers=hed)
        self.show_users()

    def show_followers(self, instance):
        layout = BoxLayout()
        layout.orientation = "vertical"
        layout.spacing = 10
        layout.size_hint_y = None
        height = 10
        for usr in self.followers['items']:
            img = base64.b64decode(usr['image'])
            data = io.BytesIO(img)
            fn = f"{usr['username']}.jpg"
            im = CoreImage(data, ext="jpg").texture
            inner_widg = Item()
            inner_widg.bg_color = (0,0,0,0.25)
            inner_widg.text = f"{usr['username']} follows you"
            inner_widg.texture = im
            inner_widg.bind(on_release=self.show_user)
            inner_widg.id = json.dumps(usr)
            layout.add_widget(inner_widg)
            height += inner_widg.height + 10
        layout.height = height
        scroller = ScrollView(size_hint_y=None, height=self.height/2)
        scroller.add_widget(layout)
        self.followers_dialog = MDDialog(
                auto_dismiss=False,
                title="Followers",
                type="custom",
                content_cls=scroller,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_press=self.close_dialog
                    )
                ],
            )
        self.followers_dialog.open()

    def show_followed(self, instance):
        layout = BoxLayout()
        layout.orientation = "vertical"
        layout.spacing = 10
        layout.size_hint_y = None
        height = 10
        scroller = ScrollView(size_hint_y=None, height=self.height/2)
        scroller.add_widget(layout)
        self.followed_dialog = MDDialog(
                auto_dismiss=False,
                title="Followed by me",
                type="custom",
                content_cls=scroller,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_press=self.close_followed_dialog
                    )
                ],
            )
        for usr in self.followed['items']:
            img = base64.b64decode(usr['image'])
            data = io.BytesIO(img)
            fn = f"{usr['username']}.jpg"
            im = CoreImage(data, ext="jpg").texture
            inner_widg = Item()
            inner_widg.bg_color = (0,0,0,0.25)
            inner_widg.text = f"You follow {usr['username']}"
            inner_widg.texture = im
            inner_widg.bind(on_release=self.show_user)
            inner_widg.id = json.dumps(usr)
            layout.add_widget(inner_widg)
            height += inner_widg.height + 10
        layout.height = height
        self.followed_dialog.open()

    def close_followed_dialog(self, instance):
        self.followed_dialog.dismiss()
    
    def close_dialog(self, instance):
        self.followers_dialog.dismiss()
    
    def close_then_open(self, instance):
        self.followers_dialog.dismiss()
        self.show_user(instance)

    def show_following():
        pass

    def show_user(self, instance):
        usr = json.loads(instance.id)
        layout = BoxLayout()
        layout.orientation = 'vertical'
        img = base64.b64decode(usr['image'])
        data = io.BytesIO(img)
        fn = f"{usr['username']}.jpg"
        im = CoreImage(data, ext="jpg").texture
        layout.add_widget(Image(texture=im))
        height = 50
        size_hint = [None, None]
        if usr['id'] in self.followed_ids:
            unfollow_button = Button(text=f"Unfollow?", height=height, size_hint=size_hint)
            unfollow_button.id = str(usr['id'])
            unfollow_button.bind(on_release=self.unfollow_user, on_press=self.close_user_dialog)
            message_button = Button(text=f"Send {usr['username']} a message?", height=height, size_hint=size_hint)
            message_button.id = json.dumps(usr)
            message_button.bind(on_release=self.create_message, on_press=self.close_user_dialog)
            layout.add_widget(unfollow_button)
            layout.add_widget(message_button)
        elif usr['id'] in self.pender_ids:
            pend_label = MDLabel(text=f"waiting for {usr['username']} to accept your request")
            layout.add_widget(pend_label)
        elif usr['id'] in self.followers_ids:
            follow_button = Button(text=f"{usr['username']} follows you, follow them back?", height=height, size_hint=size_hint)
            follow_button.id = str(usr['id'])
            follow_button.bind(on_release=self.follow_user, on_press=self.close_user_dialog)
            layout.add_widget(follow_button)
        else:
            follow_button = Button(text=f"Follow {usr['username']}", height=height, size_hint=size_hint)
            follow_button.id = str(usr['id'])
            follow_button.bind(on_release=self.follow_user, on_press=self.close_user_dialog)
            layout.add_widget(follow_button)        
        layout.height = layout.minimum_height
        scroller = ScrollView()
        scroller.height = 300
        scroller.add_widget(layout)
        self.user_dialog = MDDialog(
                auto_dismiss=False,
                title=usr['username'],
                type="custom",
                content_cls=scroller,
                buttons=[
                    MDFlatButton(
                        text="Close",
                        on_press=self.close_user_dialog
                    )
                ],
            )
        if usr['id'] in self.followed_ids:
            unfollow_button.width = self.user_dialog.width
            message_button.width = self.user_dialog.width
        elif usr['id'] not in self.pender_ids:
            follow_button.width = self.user_dialog.width
        print(self.user_dialog.width)
        self.user_dialog.open()

    def close_user_dialog(self, instance):
        self.user_dialog.dismiss()

    def create_message(self, instance):
        user = json.loads(instance.id)
        layout = BoxLayout()
        layout.orientation = 'vertical'
        title = f"Message {user['username']}"
        self.body = MDTextField(hint_text="Type your message here", multiline=True)
        send_button = Button(text='Send Message')
        send_button.size_hint_y = None
        send_button.height = 50
        send_button.bind(on_release=self.send_message, on_press=self.close_send_dialog)
        self.recipient = user['id']
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
        response = requests.post(f'https://arhat.uk/api/send/{self.recipient}/{self.user_id}/{self.body.text}', headers=hed)
        print(json.loads(response.content))

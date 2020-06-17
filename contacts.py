from __future__ import print_function

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
            contacts.add_user_widget(usr, layout)
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
        hed = {"Authorization": "Bearer " + self.token}
        response = requests.get("https://arhat.uk/api/users", headers=hed)
        self.users = json.loads(response.content)["items"]
        users = [
            user
            for user in self.users
            if self.search.text in user["username"] or self.search.text in user["email"]
        ]
        if len(self.search.text) > 0:
            search_button_text = "Reset"
        else:
            search_button_text = "Search"
        self.show_users(users=users, search_button_text=search_button_text)

    def delete_widgets(self):
        number_of_widgets = len(self.contact_scroll.children)
        for i in range(number_of_widgets):
            self.contact_scroll.remove_widget(self.contact_scroll.children[0])

    def show_users(self, users=None, search_button_text="Search"):
        self.contact_scroll = self.children[0].children[0].children[0]
        self.delete_widgets()
        self.search = MDTextField(
            id="search",
            pos_hint={"x": 0, "y": 0.62},
            size_hint_x=None,
            width=self.parent.width / 2,
        )
        self.button = MDRectangleFlatIconButton(
            id="btn",
            icon="account-search",
            pos_hint={"x": 0, "y": 0.75},
            text=search_button_text,
        )
        self.button.bind(on_release=self.search_users)
        self.followers_button = MDRectangleFlatIconButton(
            text="Followers",
            icon="account-multiple",
            pos_hint={"x": 0, "y": 0.15},
            width=self.parent.width / 2,
            id="flwr_btn",
        )
        self.followers_button.bind(on_release=self.show_follow)
        self.followed_button = MDRectangleFlatIconButton(
            text="Followed by me",
            icon="account-multiple-outline",
            width=self.parent.width / 2,
            id="flwd_btn",
            pos_hint={"x": 0, "y": 0.15},
        )
        self.followed_button.bind(on_release=self.show_follow)
        [
            self.contact_scroll.add_widget(btn)
            for btn in [
                self.search,
                self.button,
                self.followers_button,
                self.followed_button,
            ]
        ]
        hed = {"Authorization": "Bearer " + self.token}
        response = requests.get("https://arhat.uk/api/users", headers=hed)
        if not users:
            self.users = json.loads(response.content)["items"]
        else:
            self.users = users
        response = requests.get(
            f"https://arhat.uk/api/users/{self.user_id}/followers", headers=hed
        )
        self.followers = json.loads(response.content)
        self.followers_ids = [ident["id"] for ident in self.followers["items"]]
        response = requests.get(
            f"https://arhat.uk/api/users/{self.user_id}/followed", headers=hed
        )
        self.followed = json.loads(response.content)
        self.followed_ids = [ident["id"] for ident in self.followed["items"]]
        response = requests.get(
            f"https://arhat.uk/api/users/{self.user_id}/penders", headers=hed
        )
        self.penders = json.loads(response.content)
        self.pender_ids = [ident["id"] for ident in self.penders["items"]]
        layout = self.children[0].children[0].children[0]
        number_of_users = len(self.users)
        for i in range(number_of_users):
            if i == 10:
                break
            self.add_user_widget(self.users[0], layout)
            self.users.remove(self.users[0])

    def add_user_widget(self, usr, layout):
        inner_widg = Item(
            pos_hint={"x": 0, "y": 0},
            bg_color=(0, 0, 0, 0.25),
            id=json.dumps(usr),
            texture=self.get_img(usr),
        )
        if usr["id"] in self.followers_ids and usr["id"] not in self.followed_ids:
            inner_widg.text = f"{usr['username']} follows you"
        elif usr["id"] in self.followed_ids:
            inner_widg.text = f"You follow {usr['username']}"
        elif usr["id"] in self.pender_ids:
            inner_widg.text = f"Pending {usr['username']}"
        elif int(usr["id"]) != int(self.user_id):
            inner_widg.text = f"Follow {usr['username']}"
        if inner_widg.text:
            inner_widg.bind(on_release=self.show_user)
            layout.add_widget(inner_widg)

    def un_or_follow(self, id, un_or_follow):
        hed = {"Authorization": "Bearer " + self.token}
        response = requests.post(
            f"https://arhat.uk/api/{un_or_follow}/{id}/{self.user_id}", headers=hed
        )
        self.show_users()

    def show_follow(self, instance):
        if instance.id == "flwr_btn":
            users = self.followers
            text = "follows you"
            title = "Followers"
        elif instance.id == "flwd_btn":
            users = self.followed
            text = "is followed by you"
            title = "Followed by me"
        layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        height = 10
        for usr in users["items"]:
            inner_widg = Item(
                bg_color=(0, 0, 0, 0.25),
                text=f"{usr['username']} {text} ",
                texture=self.get_img(usr),
                id=json.dumps(usr),
            )
            inner_widg.bind(on_release=self.show_user)
            layout.add_widget(inner_widg)
            height += inner_widg.height + 10
        layout.height = height
        scroller = ScrollView(size_hint_y=None, height=self.height/2)
        scroller.add_widget(layout)
        self.dialog_setup(title, scroller)

    def get_img(self, usr):
        img = base64.b64decode(usr["image"])
        data = io.BytesIO(img)
        fn = f"{usr['username']}.jpg"
        im = CoreImage(data, ext="jpg").texture
        return im

    def button_setup(self, btn_text, btn_name):
        setattr(
            self,
            f"{btn_name}_button",
            Button(
                text=btn_text,
                height=self.show_user_height,
                size_hint=self.show_user_size_hint,
            ),
        )
        button_call_back = lambda _: self.un_or_follow(
            str(self.show_user_usr["id"]), btn_name
        )
        getattr(self, f"{btn_name}_button").bind(
            on_release=button_call_back, on_press=self.close_template_dialog
        )
        self.show_user_layout.add_widget(getattr(self, f"{btn_name}_button"))

    def show_user(self, instance):
        self.show_user_usr = json.loads(instance.id)
        self.show_user_layout = BoxLayout(orientation="vertical")
        self.show_user_layout.add_widget(
            Image(texture=self.get_img(self.show_user_usr))
        )
        self.show_user_height = 50
        self.show_user_size_hint = [None, None]
        if self.show_user_usr["id"] in self.followed_ids:
            self.button_setup("Unfollow?", "unfollow")
            message_button = Button(
                text=f"Send {self.show_user_usr['username']} a message?",
                height=self.show_user_height,
                size_hint=self.show_user_size_hint,
                id=json.dumps(self.show_user_usr),
            )
            message_button.bind(
                on_release=self.create_message, on_press=self.close_template_dialog
            )
            self.show_user_layout.add_widget(message_button)
        elif self.show_user_usr["id"] in self.pender_ids:
            pend_label = MDLabel(
                text=f"waiting for {self.show_user_usr['username']} to accept your request"
            )
            self.show_user_layout.add_widget(pend_label)
        elif self.show_user_usr["id"] in self.followers_ids:
            btn_text = (
                f"{self.show_user_usr['username']} follows you, follow them back?"
            )
            self.button_setup(btn_text, "follow")
        else:
            btn_text = f"Follow {self.show_user_usr['username']}"
            self.button_setup(
                self.show_user_usr, layout, btn_text, height, size_hint, "follow"
            )
        self.show_user_layout.height = self.show_user_layout.minimum_height
        scroller = ScrollView(height=300)
        scroller.add_widget(self.show_user_layout)
        self.dialog_setup(self.show_user_usr["username"], scroller)
        if self.show_user_usr["id"] in self.followed_ids:
            self.unfollow_button.width = self.template_dialog.width
            message_button.width = self.template_dialog.width
        elif self.show_user_usr["id"] not in self.pender_ids:
            self.follow_button.width = self.template_dialog.width

    def create_message(self, instance):
        user = json.loads(instance.id)
        layout = BoxLayout(orientation="vertical")
        title = f"Message {user['username']}"
        self.body = MDTextField(hint_text="Type your message here", multiline=True)
        send_button = Button(text="Send Message", size_hint_y=None, height=50)
        send_button.bind(
            on_release=self.send_message, on_press=self.close_template_dialog
        )
        self.recipient = user["id"]
        layout.add_widget(self.body)
        layout.add_widget(send_button)
        scroller = ScrollView(height=300)
        scroller.add_widget(layout)
        self.dialog_setup(title, scroller)

    def dialog_setup(self, title, scroller):
        self.template_dialog = MDDialog(
            auto_dismiss=False,
            title=title,
            type="custom",
            content_cls=scroller,
            buttons=[MDFlatButton(text="Close", on_press=self.close_template_dialog)],
        )
        self.template_dialog.open()

    def close_template_dialog(self, instance):
        self.template_dialog.dismiss()

    def send_message(self, instance):
        if self.body.text and len(self.body.text) > 0:
            hed = {"Authorization": "Bearer " + self.token}
            msg = bin(int.from_bytes(self.body.text.encode(), "big"))
            response = requests.post(
                f"https://arhat.uk/api/send/{self.recipient}/{self.user_id}/{msg}",
                headers=hed,
            )

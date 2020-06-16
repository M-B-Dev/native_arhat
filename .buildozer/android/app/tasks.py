import json
from datetime import datetime

import requests
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.color_definitions import colors
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (IconLeftWidget, MDList, OneLineAvatarListItem,
                             OneLineIconListItem)
from kivymd.uix.textfield import MDTextField
from webcolors import hex_to_rgb

from picker import MDDatePicker, MDTimePicker, ThemePicker


class Scrollable(ScrollView):
    def __init__(self, task, **kwargs):
        super(Scrollable, self).__init__(**kwargs)
        self.widg = Content(task=task)
        self.add_widget(self.widg)
        self.height = self.height*3


class Content(BoxLayout):
    def __init__(self, task, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.spacing = 20
        self.single_event_data = None
        self.id = str(task['id'])
        self.selected_color = None
        self.done_data = False
        self.page_date = task['page_date']
        self.body = MDTextField(text=task['body'], size_hint_y=None)
        self.start_time_minutes = self.set_time(task['start_time'])
        self.end_time_minutes = self.set_time(task['end_time'])
        self.start_time = Button(text=f"Start Time: {self.start_time_minutes}")
        self.start_time.size_hint_y = None
        self.start_time.height = 50
        self.start_time.bind(on_press=self.show_start_time_picker)
        self.end_time = Button(text=f"End Time: {self.end_time_minutes}")
        self.end_time.size_hint_y = None
        self.end_time.height = 50
        self.end_time.bind(on_press=self.show_end_time_picker)
        self.color = hex_to_rgb("#" + task['color'])
        self.color_pick = Button(text="Change color", background_color=(self.color[0]/255, self.color[1]/255, self.color[2]/255, .5))
        self.color_pick.bind(on_press=self.show_theme_picker)
        self.color_pick.size_hint_y = None
        self.color_pick.height = 50
        self.frequency = MDTextField(size_hint_y=None, helper_text="Frequency", helper_text_mode="persistent")
        if task['frequency']: 
            self.frequency.text=str(task['frequency'])
        if str(task['to_date']) == "None":
            self.to_date = Button(text="Enter to date")
            self.date_to = None
        else:
            self.to_date = Button(text=f"To date: {str(task['to_date'])}")
            self.date_to = task['to_date']
        self.to_date.size_hint_y = None
        self.to_date.height = 50
        self.to_date.bind(on_press=self.show_date_picker)
        self.done_label = Label(text="Done", color=(0,0,0,1))
        self.done = CheckBox()
        self.done.bind(active=self.on_checkbox_active)
        self.freq_label = Label(text="Frequency", color=(0,0,0,1))
        self.task_description_label = Label(text="Task Description", color=(0,0,0,1))
        self.add_widget(self.start_time)
        self.add_widget(self.end_time)
        self.add_widget(self.task_description_label)
        self.add_widget(self.body)
        self.add_widget(self.freq_label)
        self.add_widget(self.frequency)
        self.add_widget(self.to_date)
        self.add_widget(self.done_label)
        self.add_widget(self.done)
        self.add_widget(self.color_pick)
        if str(task['to_date']) != "None" or task['frequency'] or task['exclude']:
            self.single_event_label = Label(text="Edit just this event?", color=(0,0,0,1))
            self.single_event = CheckBox()
            self.single_event.bind(active=self.single_event_active)
            self.add_widget(self.single_event_label)
            self.add_widget(self.single_event)
        self.size_hint_y = None
        self.height = 700

    def color_picker(self, color):
        c = hex_to_rgb("#" + colors[color]["900"])
        self.selected_color = colors[color]["900"]
        self.color_pick.background_color = (c[0]/255, c[1]/255, c[2]/255, 0.5)

    def show_theme_picker(self, instance):
        self.theme_dialog = ThemePicker(id=self.id)
        self.theme_dialog.open()

    def on_color(self, instance, value):
        self.color = str(instance.hex_color)

    def get_to_date(self, date):
        '''
        :type date: <class 'datetime.date'>
        '''
        self.date_to = datetime.strftime(date, "%d-%m-%Y")
        self.to_date.text = f"Date to: {self.date_to}"

    def show_date_picker(self, instance):
        date_dialog = MDDatePicker(callback=self.get_to_date)
        date_dialog.open()

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.done_data = True


    def single_event_active(self, checkbox, value):
        if value:
            self.single_event_data = True

    def show_start_time_picker(self, instance):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_start_time)
        time_dialog.open()

    def get_start_time(self, instance, time):
        self.start_time_minutes = time
        self.start_time.text = f"Start Time: {str(self.start_time_minutes)}"

    def show_end_time_picker(self, instance):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_end_time)
        time_dialog.open()

    def get_end_time(self, instance, time):
        self.end_time_minutes = time
        self.end_time.text = f"End Time: {str(self.end_time_minutes)}"

    def set_time(self, time):
        if time > 599:
            hour = str(time/60)[0:2]
        else:
            hour = f"0{str(time/60)[0:1]}"
        minutes = time - (int(hour)*60)
        if minutes > 9:
            return f"{hour}:{minutes}"
        else:
            return f"{hour}:0{minutes}"

class ImageButton(ButtonBehavior, Image):
    def __init__(self, task, inst, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.text='test'
        self.size_hint_y = None
        self.size_hint_x = None
        self.task = task
        self.inst = inst
        self.on_press = lambda *args: self.show_edit_task()
        with self.canvas.before:
            self.lbl_staticText = Label(font_size=12, color=(0,0,0,1)) 
            self.lbl_staticText.text = f"{task['body']}: Start time: {self.set_time(task['start_time'])} Finish time: {self.set_time(task['end_time'])}"
            self.lbl_staticText.texture_update()
            self.lbl_staticText.pos = self.pos
            self.lbl_staticText.size = self.size

    def show_edit_task(self):
        self.edit_task = MDDialog(
                auto_dismiss=False,
                title="Edit task:",
                type="custom",
                content_cls=Scrollable(task=self.task),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_press=self.close_dialog
                    ),
                    MDFlatButton(
                        text="OK",
                        on_press=self.update_task
                    ),
                ],
            )
        self.edit_task.create_items()
        self.edit_task.open()

    def close_dialog(self, instance):
        self.edit_task.dismiss()

    def update_task(self, instance):
        if self.edit_task:
            body = self.edit_task.content_cls.widg.body.text
            start_minutes = (int(str(self.edit_task.content_cls.widg.start_time_minutes)[0:2])*60) + int(str(self.edit_task.content_cls.widg.start_time_minutes)[-2])
            end_minutes = (int(str(self.edit_task.content_cls.widg.end_time_minutes)[0:2])*60) + int(str(self.edit_task.content_cls.widg.end_time_minutes)[-2])
            frequency = self.edit_task.content_cls.widg.frequency.text
            if not frequency:
                frequency = 0
            date_to = self.edit_task.content_cls.widg.date_to
            done = self.edit_task.content_cls.widg.done_data
            single_event = self.edit_task.content_cls.widg.single_event_data
            page_date = self.edit_task.content_cls.widg.page_date
            if self.edit_task.content_cls.widg.selected_color:
                color = self.edit_task.content_cls.widg.selected_color
            else:
                color = self.task['color']
            data = {
                'color': color,
                'body': body, 
                'done': done, 
                'start_time': start_minutes, 
                'end_time': end_minutes, 
                'frequency': frequency, 
                'to_date': date_to, 
                'single_event': single_event,
                'page_date': page_date
            }
            hed = {'Authorization': 'Bearer ' + self.inst.token}
            response = requests.put(f'https://arhat.uk/api/tasks/{self.task["id"]}', json=data, headers=hed)
            if self.parent:
                original_widgets = [child for child in self.parent.children if "ImageButton" in str(type(child))]
                self.parent.load_tasks()
                for child in original_widgets:
                    if self.parent:
                        self.parent.remove_widget(child)
            self.edit_task.dismiss()


    def set_time(self, time):
        if time > 599:
            hour = str(time/60)[0:2]
        else:
            hour = f"0{str(time/60)[0:1]}"
        minutes = time - (int(hour)*60)
        if minutes > 9:
            return f"{hour}:{minutes}"
        else:
            return f"{hour}:0{minutes}"

class Tasks(Screen):
    tasks = ObjectProperty(None)
    token = ObjectProperty(None)
    user_id = ObjectProperty(None)
  
        
    def load_tasks(self, date=datetime.strftime(datetime.today(), "%d-%m-%Y"), height=None, width=None, manager=None):
        self.date = date
        if not width:
            width = self.parent.width
        if not height:
            height = self.parent.height
        if manager:
            self.manager = manager
        hed = {'Authorization': 'Bearer ' + self.token}
        user_tasks = requests.get(f'https://arhat.uk/api/tasks/{self.user_id}/{date}', headers=hed)
        self.tasks = json.loads(user_tasks.content)['items']
        task_width = width * 0.75
        for task in self.tasks:
            task['page_date'] = self.date
            color = hex_to_rgb("#" + task['color'])
            button = ImageButton(
                inst=self,
                task=task, 
                pos=(
                    (width/2)-(task_width/2), 
                    height - (int(task['end_time']))/3
                    ), 
                size=(task_width,(int(task['end_time'])-int(task['start_time']))/3), 
                color=(color[0]/255, color[1]/255, color[2]/255, .5), 
                source=None
                )
            setattr(self, str(task['id']), button)
            self.add_widget(getattr(self, str(task['id'])))
        self.date_button = Button(text=f"Change date: {self.date}", pos=(width/2-250, 0), size_hint_y=None, size_hint_x=None, size=(500, 50))
        self.date_button.bind(on_press=self.show_date_picker)
        self.add_widget(self.date_button)
        self.manager.current = "Tasks"

    def get_date(self, date):
        '''
        :type date: <class 'datetime.date'>
        '''
        self.date = datetime.strftime(date, "%d-%m-%Y")
        
        original_widgets = [child for child in self.children if "ImageButton" in str(type(child))]
        self.load_tasks(date=self.date)
        for child in original_widgets:
            self.remove_widget(child)

    def show_date_picker(self, instance):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()

    def set_time(self, time):
        if time > 599:
            hour = str(time/60)[0:2]
        else:
            hour = f"0{str(time/60)[0:1]}"
        minutes = time - (int(hour)*60)
        if minutes > 9:
            return f"{hour}:{minutes}"
        else:
            return f"{hour}:0{minutes}"

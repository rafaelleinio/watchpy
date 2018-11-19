import socket
import abc
import os
import glob
import subprocess

from kivy.config import Config
from kivy.core.window import Window
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
import pygame
import cv2

import utils
import plate

Config.set('graphics', 'resizable', 0)
win_x = 854
win_y = 600
crop_px = 30
Window.size = (win_x, win_y)
kv = '''
main:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint: [1,.80]
            ImageButton:
                id: image_source
                source: 'foo.png'
                on_press: root.image_onPress()
        BoxLayout:
            size_hint: [1,.20]
            GridLayout:
                cols: 5
                spacing: '10dp'
                padding: '10dp'
                Button:
                    id: automatic_ai
                    text:'Automatic AI'
                    bold: True
                    on_press: root.automatic_ai()
                Button:
                    id: status
                    text:'Play'
                    bold: True
                    on_press: root.playPause()
                GridLayout:
                    cols: 1
                    ToggleButton:
                        id: toggle_image
                        text: 'Image File'
                        state: 'down'
                        group: 'toggle'
                    ToggleButton:
                        id: toggle_video
                        text: 'Video File'
                        group: 'toggle'
                    ToggleButton:
                        id: toggle_stream
                        text: 'Web Stream'
                        group: 'toggle'
                Button:
                    text: 'Setting'
                    bold: True
                    on_press: root.setting()
                Button:
                    text: 'Close'
                    bold: True
                    on_press: root.close()
<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"

        FileChooserIconView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancela"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)

<SaveDialog>:
    text_input: text_input
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserListView:
            id: filechooser
            on_selection: text_input.text = self.selection and self.selection[0] or ''
 
        TextInput:
            id: text_input
            size_hint_y: None
            height: 30
            multiline: False
 
        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()
 
            Button:
                text: "Salvar"
                on_release: root.save(filechooser.path, text_input.text)
'''


class ImageButton(ButtonBehavior, Image):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_press(self):
        """Define an action to be executed when
        click on the image"""


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)



class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class main(BoxLayout):
    # stream atributes
    ipAddress = None
    port = None
    
    # video/image files player atributes
    video_file = None
    i_frame = 0
    image_file = None

    # sr opt atributes
    sr_bool = False

    # load/save file atributes
    text_input = ObjectProperty(None) 
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    
    # imagem processing methods
    def image_onPress(self):
        if self.sr_bool is False:
            # get mouse coordinates
            x, y = utils.xy_calc(Window.mouse_pos)
            
            # assert x, y
            x = utils.clamp(x, crop_px, win_x - crop_px)
            y = utils.clamp(y, crop_px, win_y - crop_px)
            
            # crop around mouse position
            image = utils.open_image('foo.png')
            image = utils.crop_image(image, int(x), int(y), crop_px)
            utils.save_image('tmp/crop_little.png', image)
            image = utils.click_resize_image(image, 8)
            utils.save_image('tmp/crop.png', image)

            # building popup
            box_popup = GridLayout(cols=1)
            box_image = GridLayout(cols=1, size_hint=(1, .8))
            img_widget = Image(id='imagem', source='tmp/crop.png')
            img_widget.reload()
            box_image.add_widget(img_widget)
            box_popup.add_widget(box_image)
            box_control = GridLayout(cols=5, size_hint=(1, .2))
            btn1 = Button(text="Detect Plate", bold=True)
            btn2 = Button(text="SR - Face", bold=True)
            btn3 = Button(text="SR - Text", bold=True)
            btn4 = Button(text="Save Image", bold=True)
            btn5 = Button(text="Close", bold=True)
            btn1.bind(on_press=self.pop_up_get_plate)
            btn2.bind(on_press=self.sr_face)
            btn3.bind(on_press=self.sr_text)
            btn4.bind(on_press=self.show_save)
            btn5.bind(on_press=self.close_popup_crop)
            box_control.add_widget(btn1)
            box_control.add_widget(btn2)
            box_control.add_widget(btn3)
            box_control.add_widget(btn4)
            box_control.add_widget(btn5)
            box_popup.add_widget(box_control)

        else:
            print(self.sr_bool)
            # building popup
            box_popup = GridLayout(cols=1)
            box_image = GridLayout(cols=1, size_hint=(1, .8))
            img_widget = Image(id='imagem', source='tmp/crop.png')
            img_widget.reload()
            box_image.add_widget(img_widget)
            box_popup.add_widget(box_image)
            box_control = GridLayout(cols=3, size_hint=(1, .2))
            btn1 = Button(text="Detect Plate", bold=True)
            btn2 = Button(text="Save Image", bold=True)
            btn3 = Button(text="Close", bold=True)
            btn1.bind(on_press=self.pop_up_get_plate)
            btn2.bind(on_press=self.show_save)
            btn3.bind(on_press=self.close_popup_crop)
            box_control.add_widget(btn1)
            box_control.add_widget(btn2)
            box_control.add_widget(btn3)
            box_popup.add_widget(box_control)

        # creating popup
        self.popup_crop = Popup(
            title='Image', content=box_popup, size=(384, 480))
        self.popup_crop.open()

    def close_popup_crop(self, btn):
        self.sr_bool = False
        self.popup_crop.dismiss()

    def sr_face(self, btn):
        image = utils.open_image('tmp/crop_little.png')
        utils.save_image('model/dcscn_faces/crop_little.png', image)
        os.system('cd model/dcscn_faces && python sr.py --file=crop_little.png --batch_image_size=16 --layers=18 --filters=196 --training_images=200000 --scale=8')
        image = utils.open_image('model/dcscn_faces/output/dcscn_L18_F196to48_Sc8_NIN_A64_PS_R1F32/crop_little_result.png')
        utils.save_image('tmp/crop.png', image)
        self.sr_bool = True
        self.popup_crop.dismiss()
        self.image_onPress()

    def sr_text(self, btn):
        image = utils.open_image('tmp/crop_little.png')
        utils.save_image('model/dcscn_text/crop_little.png', image)
        os.system('cd model/dcscn_text && python sr.py --file=crop_little.png --batch_image_size=18 --layers=18 --filters=196 --training_images=100000 --scale=8')
        image = utils.open_image('model/dcscn_text/output/dcscn_L18_F196to48_Sc8_NIN_A64_PS_R1F32/crop_little_result.png')
        utils.save_image('tmp/crop.png', image)
        self.sr_bool = True
        self.popup_crop.dismiss()
        self.image_onPress()

    def pop_up_get_plate(self, btn):
        if self.sr_bool is False:
            plate.get_plate('tmp/crop_little.png')
        else:
            plate.get_plate('tmp/crop.png')

    def automatic_ai(self):
        image = utils.open_image('foo.png')
        image = utils.resize_image(image, 1280, 720)
        utils.save_image('model/CAR/input.jpg', image)
        os.system('cd model/CAR && python main.py input.jpg yolo')
        image = utils.open_image('model/CAR/result.jpg')
        image = utils.resize_image(image, 854, 480)
        utils.save_image('foo.png', image)
        self.ids.image_source.reload()
        
        positions = utils.get_car_positions()
        print('Cars positions: ' + str(positions))

        for car in glob.glob('model/CAR/cars/*.png'):
            print('Start Processing for: ' + car)
            plate.get_plate(car)
        
        utils.clean_cars_folder()

    # Image/video load/save  methods
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Open File", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        if(self.ids.toggle_video.state == 'down'):
            # video path
            self.video_file = os.path.join(path, filename[0])
            # clean tmp frames folder
            files = glob.glob('tmp/frames/*')
            for f in files:
                os.remove(f)
            # loading the frames of the video
            cap = cv2.VideoCapture(self.video_file)
            currentFrame = 0
            while(True):
                # Capture frame-by-frame
                ret, frame = cap.read()
                # if not ret:
                #    break
                if currentFrame > 500:
                    break
                # Saves image of the current frame in png file
                name = 'tmp/frames/' + str(currentFrame) + '.png'
                print('Creating...' + name)
                utils.save_image(name, frame)

                # To stop duplicate images
                currentFrame += 1
            cap.release()

        if(self.ids.toggle_image.state == 'down'):
            # image path
            self.image_file = os.path.join(path, filename[0])
            image = utils.open_image(self.image_file)
            
            # refresh image viewer widget
            utils.save_image('foo.png', image)
            self.ids.image_source.reload()
        self.dismiss_popup()

    def show_save(self, btn):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        image = utils.open_image('tmp/crop.png')
        utils.save_image(os.path.join(path, filename), image)

        self.dismiss_popup()

    def recv_frame(self, dt):
        frame = utils.get_frame(self.i_frame)
        print(frame.shape)
        if (frame is not None):
            utils.save_image('foo.png', frame)
            self.ids.image_source.reload()
            self.i_frame += 1
        else:
            self.i_frame = 0

    # streamming method
    def recv_socket(self, dt):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((self.ipAddress, self.port))
        received = []
        while True:
            recvd_data = clientsocket.recv(230400)
            if not recvd_data:
                break
            else:
                received.append(recvd_data)
        dataset = b''.join(received)
        # convert received image from bytes
        image = pygame.image.fromstring(dataset, (640, 480), "RGB")
        try:
            pygame.image.save(image, "foo.png")
            self.ids.image_source.reload()
        except:
            pass

    # video play/pause methods
    def playPause(self):
        # Stream option
        if(self.ids.toggle_stream.state == 'down'):
            if self.ipAddress is None or self.port is None:
                box = GridLayout(cols=1)
                box.add_widget(Label(text="Ip or Port Not Set"))
                btn = Button(text="OK")
                btn.bind(on_press=self.closePopup)
                box.add_widget(btn)
                self.popup1 = Popup(
                    title='Error', content=box, size_hint=(.8, .3))
                self.popup1.open()
            else:
                if self.ids.status.text == "Stop":
                    self.stop()
                else:
                    self.ids.status.text = "Stop"
                    Clock.schedule_interval(self.recv_socket, 0.1)
        
        # Video option
        elif(self.ids.toggle_video.state == 'down'):
            if self.video_file is None:
                print(">>>>> there is no file path")
                box = GridLayout(cols=1)
                box.add_widget(Label(text="File Path Not Set"))
                btn = Button(text="OK")
                btn.bind(on_press=self.closePopup)
                box.add_widget(btn)
                self.popup1 = Popup(
                    title='Error', content=box, size_hint=(.8, .3))
                self.popup1.open()
            else:
                if self.ids.status.text == "Stop":
                    self.stop()
                else:
                    self.ids.status.text = "Stop"
                    Clock.schedule_interval(self.recv_frame, 0.03)
        
        # Image option
        elif(self.ids.toggle_video.state == 'down'):
            if self.ids.status.text == "Stop":
                    self.stop()
            else:
                self.ids.status.text = "Stop"
                self.ids.image_source.reload()

    def closePopup(self, btn):
        self.popup1.dismiss()

    def stop(self):
        self.ids.status.text = "Play"
        Clock.unschedule(self.recv_frame)
        Clock.unschedule(self.recv_socket)

    # other functions
    def close(self):
        utils.clean_tmp_folder()
        App.get_running_app().stop()

    def setting(self):
        if(self.ids.toggle_stream.state == 'down'):
            box = GridLayout(cols=2)
            box.add_widget(Label(text="IpAddress: ", bold=True))
            self.st = TextInput(id="serverText")
            box.add_widget(self.st)
            box.add_widget(Label(text="Port: ", bold=True))
            self.pt = TextInput(id="portText")
            box.add_widget(self.pt)
            btn = Button(text="Set", bold=True)
            btn.bind(on_press=self.settingProcess)
            box.add_widget(btn)
            self.popup = Popup(
                title='Stream Settings', content=box, size_hint=(.6, .4))
            self.popup.open()

        elif(self.ids.toggle_video.state == 'down' or self.ids.toggle_image.state == 'down'):
            self.show_load()

    def settingProcess(self, btn):
        try:
            self.ipAddress = self.st.text
            self.port = int(self.pt.text)
        except:
            pass
        self.popup.dismiss()


class Watchpy(App):
    def build(self):
        return Builder.load_string(kv)


Watchpy().run()

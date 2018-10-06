import socket
import abc
import os
import glob
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
import utils
import cv2

Config.set('graphics', 'resizable', 0)
Window.size = (640, 600)
kv = '''
main:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint: [1,.80]
            ImageButton:
                id: image_source
                source: 'foo.jpg'
                on_press: root.image_onPress()
        BoxLayout:
            size_hint: [1,.20]
            GridLayout:
                cols: 5
                spacing: '10dp'
                padding: '10dp'
                Button:
                    id: status
                    text:'Play'
                    bold: True
                    on_press: root.playPause()
                GridLayout:
                    cols: 1
                    ToggleButton:
                        id: toggle_file
                        text: 'Video File'
                        state: 'down'
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


class main(BoxLayout):
    ipAddress = None
    port = None
    video_file = None
    i_frame = 0

    # crop imagem methods
    def image_onPress(self):
        # processing the image
        x, y = utils.xy_calc(Window.mouse_pos)
        image = utils.open_image('foo.jpg')
        image = utils.crop_image(image, int(x), int(y), 24)
        image = utils.resize_image(image, 8)
        print(image)
        utils.save_image('tmp/crop.jpg', image)

        # building popup
        box_popup = GridLayout(cols=1)

        box_image = GridLayout(cols=1, size_hint=(1, .8))
        img_widget = Image(source='tmp/crop.jpg')
        img_widget.reload()
        box_image.add_widget(img_widget)
        box_popup.add_widget(box_image)

        box_control = GridLayout(cols=3, size_hint=(1, .2))
        btn1 = Button(text="Super Resolution", bold=True)
        btn2 = Button(text="Save Image", bold=True)
        btn3 = Button(text="Close", bold=True)
        btn3.bind(on_press=self.close_popup_crop)
        # btn2.bind(on_press=u
        box_control.add_widget(btn1)
        box_control.add_widget(btn2)
        box_control.add_widget(btn3)
        box_popup.add_widget(box_control)

        # creating popup
        self.popup_crop = Popup(
            title='Image', content=box_popup, size=(384, 480))
        self.popup_crop.open()

    def close_popup_crop(self, btn):
        self.popup_crop.dismiss()

    # video file methods
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Open File", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
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
            # Saves image of the current frame in jpg file
            name = './tmp/frames/' + str(currentFrame) + '.jpg'
            print('Creating...' + name)
            cv2.imwrite(name, frame)

            # To stop duplicate images
            currentFrame += 1
        cap.release()
        self.dismiss_popup()

    def recv_frame(self, dt):
        frame = utils.get_frame(self.i_frame)
        if (frame is not None):
            utils.save_image('foo.jpg', frame)
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
            pygame.image.save(image, "foo.jpg")
            self.ids.image_source.reload()
        except:
            pass

    # video play/pause methods
    def playPause(self):
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

        elif(self.ids.toggle_file.state == 'down'):
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

    def closePopup(self, btn):
        self.popup1.dismiss()

    def stop(self):
        self.ids.status.text = "Play"
        Clock.unschedule(self.recv_frame)
        Clock.unschedule(self.recv_socket)

    # other functions
    def close(self):
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
        elif(self.ids.toggle_file.state == 'down'):
            self.show_load()

    def settingProcess(self, btn):
        try:
            self.ipAddress = self.st.text
            self.port = int(self.pt.text)
        except:
            pass
        self.popup.dismiss()


class videoStreamApp(App):
    def build(self):
        return Builder.load_string(kv)


videoStreamApp().run()

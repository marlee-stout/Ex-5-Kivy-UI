import os

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.slider import Slider
from kivy.animation import Animation

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
import time

from pidev.Joystick import Joystick
from threading import Thread
from time import sleep

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'
SCREEN_TWO_NAME = "screen_two"

joystick = Joystick(0, False)

class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White


class MainScreen(Screen):

    string_value = StringProperty()
    motor_value = StringProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.count = 0
        self.motor_value = "Off"
        self.anim = ()


    """
    Class to handle the main screen and its associated touch events
    """

    def pressed(self):
        """
        Function called on button touch event for button with id: testButton
        :return: None
        """
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='admin', text="Test", pause_duration=5)

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    def counter(self):
        self.string_value = str(self.count)
        self.count = self.count + 1

    def motor_switch(self):
        if self.motor_value == "On":
            self.motor_value = "Off"
        else:
            self.motor_value = "On"

    def change_screens(self):
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='screen_two', text="Test", pause_duration=1)

    def animate(self):
        self.anim = Animation(x=.1, y=.1) & Animation(size=(200, 200))
        self.anim.start(self.ids.screen_two_button)


class ScreenTwo(Screen):

    joystick = Joystick(0, True)
    button_state = ObjectProperty(0)

    def __init__(self, **kwargs):
        Builder.load_file('ScreenTwo.kv')
        super(ScreenTwo, self).__init__(**kwargs)
        self.anim = ()


    def go_back(self):
        PauseScreen.pause(pause_scene_name='pauseScene', transition_back_scene='main', text="Test",
                          pause_duration=1)

    def animate(self):
        self.anim = Animation(x=.1, y=.1) & Animation(size=(400, 200))
        self.anim.start(self.ids.animate_button)

    def joy_update(self):
        while 1:
            self.ids.joystick.center_x = joystick.get_axis('x') * self.width

            self.ids.joystick.center_y = joystick.get_axis('y') * -self.height

            self.ids.joystick.text = "{:.3f} {:.3f}".format(joystick.get_axis('x'), joystick.get_axis('y'))

            self.button_state = self.joystick.get_button_state(0)
            sleep(.1)

    def start_joy_thread(self):
        Thread(target=self.joy_update, args=()).start()


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game" is pressed

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()
"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(ScreenTwo(name=SCREEN_TWO_NAME))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()

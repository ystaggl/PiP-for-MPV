"""
Module for creating floating window (Picture-in-Picture) players in python.
You can set the player by calling the set_player function, e.g. PipPy.set_player("mpv"), by default it uses mpv.

This project is deprecated. It was one of the first of my old scripts I remade in python, and hasn't been touched in a long time. The code is not great.
Looking at it really makes me want to rewrite it, but it's functionality is better produced with simple mpv config changes,
as mpv already has most of this functionality built in.

Instead, I thought it'd be fun to add some annotated comments. So if anyone's reading this, hi.
"""
import os
import ctypes
import ctypes.wintypes
import win32gui
import win32con
import keyboard
import time
import atexit
from python_mpv_jsonipc import MPV, MPVError
from multiprocessing.connection import Client
from win32api import GetKeyState
from win32con import VK_SCROLL

#Why am I using global variables as config options?
require_scroll = True
use_logitech_lighting = True #This relates to LogiPy, a project I worked on simultaneously.

#These aren't even config options but toggles changed by functions in the script. This is not good.
window_handle = None
size_box = False #Toggle if the window is resizeable
autoplay = False
mpv_error = False #Tracks if there's been an error I guess? This is not good error handling.

user32 = ctypes.windll.user32 #for setting window styles (i.e. borderless)

#Global Variable Defaults 
player_class = "mpv"
#This was meant to set differnt positions depending on if the monitor was vertical, but it requires that you're using 1920x1080 or 1080x1920. This was bad code.
if  user32.GetSystemMetrics(0) == 1080:
    (floating_posx,floating_posy,floating_width,floating_height) = (594,1310,323,565)
else:
    (floating_posx,floating_posy,floating_width,floating_height) = (1310,594,565,323)
    (default_posx,default_posy,default_width,default_height) = (312,125,1296,759)




#Functions to change defaults.
#TODO: Change these functions so they create ini files
# ^ Good idea, I should've done it before this project became obsolete.


def set_player(new_player_class):
    """
    Change which media player this script uses, by default it is mpv.
    The input should be a window class, see https://docs.microsoft.com/en-us/windows/win32/winmsg/about-window-classes#application-global-classes
    Currently Unused.
    """
    global player_class
    player_class = new_player_class
    return f"Set {player_class} as the media player"


def set_floating_position(new_position):
    """
    Accepts a length 4 tuple (PosX,PosY,Width,Height)
    Set the position and dimensions of the player when it is a floating window. 
    Currently Unused.
    """
    global floating_posx
    global floating_posy
    global floating_width
    global floating_height
    (floating_posx,floating_posy,floating_width,floating_height) = (new_position)


def set_default_position(new_position):
    """
    Accepts a length 4 tuple (PosX,PosY,Width,Height)
    Set the position and dimensions of the player when it is reset. 
    Currently Unused.
    """
    global default_posx
    global default_posy
    global default_width
    global default_height
    (default_posx,default_posy,default_width,default_height) = (new_position)


#Functions that modify the player window
def sizebox_toggle(window_class=player_class):
    """
    Toggles whether the window has a resizing border (Lets you resize by dragging the corner)
    """
    print("sizebox_toggle()")
    #For using scroll lock to enable/disable the hotkeys
    if require_scroll and not GetKeyState(VK_SCROLL):
        return
    global size_box
    size_box = not size_box
    multiplier = 2 * int(size_box) - 1 #Converts True to -1 and False to 1. This was an oversimplification.
    style = user32.GetWindowLongPtrA(window_handle,win32con.GWL_STYLE) + ((multiplier) * win32con.WS_SIZEBOX) #Set style variable to current window style with sizebox toggled
    user32.SetWindowLongPtrA(window_handle,win32con.GWL_STYLE,style) #sets window style flags to match the new style variable
    return



def set_floating_window(window_class=player_class):
    """
    Sets the player window to a floating window. Also sets the handle of the player window which is used by other functions.
    """
    if require_scroll and not GetKeyState(VK_SCROLL):
        return

    global mpv_error
    global floating_width
    global window_handle
    global size_box
    global floating_height
    window_handle = win32gui.FindWindowEx(None,None,window_class,None)

    #Switches the window to it's floating size.
    new_height = floating_height
    new_width = floating_width
    new_posy = floating_posy

    #this tries to get the x and y coordinates by asking mpv itself, but that functionality was broken when I stopped working on the project.
    #Instead it uses the display resolution from windows api and does some weird math with magic numbers that I no longer understand.
    if not mpv_error:
        try:
            #TODO: FIX
            #mpv = MPV(start_mpv=False, ipc_socket="mpvsocket")
            #width = mpv.command("get_property","width")
            #height = mpv.command("get_property","height")
            
            
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            new_width = round(width/height * floating_height)
            if round(width/height*3) == 4:
                new_posy -= 30
                new_height = round(new_height*1.2)
                new_width = round(new_width*1.2)

        except MPVError:
            print("Can't connect to mpv, using default values")
            mpv_error = True
    
    
    #TODO: FIX
    user32.SetWindowPos(window_handle,ctypes.wintypes.HWND(win32con.HWND_TOPMOST),floating_posx,new_posy,new_width,new_height,0)
    user32.SetWindowLongPtrA(window_handle,win32con.GWL_STYLE,335740928) #335740928 corresponds to a window without 0x800000, 0x400000, 0x80000, or 0x40000. Those are window style flags by the way.
    size_box = False
    return


def reset_window(window_class=player_class):
    """
    Reset the player window to a normal window.
    """
    if require_scroll and not GetKeyState(VK_SCROLL):
        return
    global mpv_error
    global window_handle
    global size_box

    if mpv_error:
        (posx,posy,width,height) = (default_posx,default_posy,default_width,default_height)

    else:
        try:
            #TODO: FIX
            mpv = MPV(start_mpv=False, ipc_socket="mpvsocket")
            #width = mpv.command("get_property","width")
            #height = mpv.command("get_property","height")
            #posx = round((1920-width)/2)
            #posy = round((1080-height)/2)
        except MPVError:
            print("Can't connect to mpv, using default values")
            mpv_error = True
            (posx,posy,width,height) = (default_posx,default_posy,default_width,default_height)

    #TODO: FIX
    #user32.SetWindowPos(window_handle,ctypes.wintypes.HWND(win32con.HWND_NOTOPMOST),posx,posy,width,height,0)
    user32.SetWindowLongPtrA(window_handle,win32con.GWL_STYLE,349110272)
    size_box = False
    return


def toggle_autoplay():
    """
    Toggles whether the video player automatically plays the next video in folder.
    This function is a mess.
    """
    global use_logitech_lighting
    if require_scroll and not GetKeyState(VK_SCROLL):
        return
    if player_class != "mpv":
        return
    global autoplay
    autoplay = not autoplay
    try:
        mpv = MPV(start_mpv=False, ipc_socket="mpvsocket")
    except MPVError:
        print("Cannot connect to mpv")
        autoplay_lighting(False)
    if autoplay:
        autoplay_lighting(True)
        video_path = mpv.command("get_property","path")
        try:
            filename_index = video_path.rindex("\\") + 1
        except ValueError:
            print("Can't toggle autoplay for this file")
            return
        media_directory = video_path[:filename_index]
        file_queue = os.listdir(video_path[0:filename_index])
        file_queue = file_queue[file_queue.index(video_path[filename_index:]):]
        for files in file_queue:
            files = f"{media_directory}{files}"
            mpv.loadfile(files,"append-play")
        return
    mpv.playlist_clear()
    autoplay_lighting(False)
    return


def autoplay_lighting(autoplay):
    """
    This function I wrote for myself back when I made this program, it causes it to send commands to a separate python script I made to control the Logitech lighting SDK. (called 'LogiPy')
    Honestly this isn't really useful to anyone.
    Set lighting for F4 key based on whether next episodes will autoplay.
    """
    global use_logitech_lighting
    if not use_logitech_lighting:
        print("Logitech Lighting has been disabled for this instance, due to too many failed attempts")
        return
    
    if require_scroll and not GetKeyState(VK_SCROLL):
        return

    #This was my first attempt at inter-process communication.
    address = ('localhost', 6001)
    try:
        conn = Client(address, authkey=b'LogiLed')
    except (ConnectionResetError, ConnectionRefusedError):
        error_count = 1
        connection_error = True
        while connection_error:
            error_count += 1
            time.sleep(1)
            try:
                conn = Client(address, authkey=b'LogiLed')
                connection_error = False
            except (ConnectionResetError, ConnectionRefusedError):
                connection_error = True
            if error_count >= 10:
                use_logitech_lighting = False
                print("Couldn't establish a connection after 10 retries. Cancelling colour change.")
                return

    if autoplay:
        conn.send("'SetLightingForKeyWithKeyName',('F4',99,1,24)")
    else:
        conn.send("'SetLightingForKeyWithKeyName',('F4',0,56,88)")
    return


def exit_handler():
    """
    Exit Function, shuts down Logitech Illumination SDK so that it doesn't interfere with other programs.
    """
    autoplay_lighting.conn.close()
atexit.register(exit_handler)


if __name__ == "__main__":
    #This is where you can adjust hotkeys.
    keyboard.add_hotkey("F1",lambda: sizebox_toggle())
    keyboard.add_hotkey("F2",lambda: set_floating_window())
    keyboard.add_hotkey("F3",lambda: reset_window())
    keyboard.add_hotkey("F4",lambda: toggle_autoplay())
    keyboard.wait()

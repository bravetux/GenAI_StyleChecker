import os
from tkinter import END
from tkinter import messagebox

def threadsafe_gui(master, func):
    """Calls the given function in the main thread of the given master widget,
    allowing it to safely modify Tkinter widgets even if called from another thread."""
    master.after(0, func)

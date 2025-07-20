import os
from tkinter import END
from tkinter import messagebox

def threadsafe_gui(master, func):
    """Calls the given function in the main thread of the given master widget,
    allowing it to safely modify Tkinter widgets even if called from another thread.

    Tkinter is not thread-safe.  If you try to modify widgets from another thread,
    you can get strange errors or things can just not work.  To avoid this, we use
    the after method to schedule the function to run in the main thread.
    """
    master.after(0, func)

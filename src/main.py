import sys
from tkinter import Tk
from gui import StyleCheckerApp

def main():
    """
    Initializes the main application window for the C# Style Checker GUI.

    Sets up the Tkinter root window and creates an instance of the StyleCheckerApp,
    which provides the user interface and functionality for checking C# files
    against the Google C# Style Guide. Runs the Tkinter main event loop to
    keep the application responsive to user interactions.
    """

    root = Tk()
    app = StyleCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
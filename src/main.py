import sys
from tkinter import Tk
from gui import StyleCheckerApp

def main():
    """
    Main function to initialize and run the Language Style Checker GUI application.

    This function sets up the main application window using Tkinter, creates an
    instance of the StyleCheckerApp class, and starts the Tkinter event loop to
    handle user interactions with the GUI.
    """

    # Create the main window using Tkinter's Tk class
    root = Tk()

    # Create an instance of the StyleCheckerApp class, passing the root window
    # This sets up the user interface and functionality for style checking
    app = StyleCheckerApp(root)

    # Enter the Tkinter main event loop to keep the application running
    # and responsive to user interactions
    root.mainloop()

if __name__ == "__main__":
    main()
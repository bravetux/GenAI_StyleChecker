from tkinter import Tk, Button, Label, filedialog, messagebox, Text, Scrollbar, END, Entry, StringVar, OptionMenu, Frame

def setup_gui(master, app):
    """
    Sets up the GUI layout and components for the StyleCheckerApp.

    Args:
        master: The root window or parent widget for the application.
        app: The instance of the StyleCheckerApp to bind components to.
    """
    print("Setting up GUI layout...")  # Debug: Log GUI setup start
    master.title("C# Style Checker")
    master.geometry("762x600")  # Main window size

    consolas_font = ("Consolas", 14)

    # Frame for folder input and buttons
    top_frame = Frame(master)
    top_frame.pack(fill='x')

    # Align Folder to Scan text boxes
    folder_frame = Frame(master)
    folder_frame.pack(fill='x')

    Label(folder_frame, text="Folder to Scan:", font=consolas_font).pack(side='left')
    app.folder_entry = Entry(folder_frame, width=50, font=consolas_font)
    app.folder_entry.pack(side='left', padx=5)
    Button(folder_frame, text="Browse", command=app.select_folder, font=consolas_font).pack(side='left')

    # Buttons on a new line
    button_frame = Frame(master)
    button_frame.pack(fill='x')
    Button(button_frame, text="Scan Files", command=app.scan_files, font=consolas_font).pack(side='left', padx=10)
    Button(button_frame, text="Check Style", command=app.check_style, font=consolas_font).pack(side='left', padx=10)
    Button(button_frame, text="Update Ollama Model", command=app.update_model_list, font=consolas_font).pack(side='left', padx=10)
    # Exit button relocated to bottom frame

    # LLM model dropdown with label
    model_frame = Frame(master)
    model_frame.pack(fill='x')
    Label(model_frame, text="Ollama Models:", font=consolas_font).pack(side='left')
    app.model_var = StringVar(master)
    app.model_var.set("Select Model")
    app.model_dropdown = OptionMenu(model_frame, app.model_var, "")
    app.model_dropdown.config(font=consolas_font)
    app.model_dropdown.pack(side='left')

    # Add Language Dropdown next to the Ollama Model Dropdown
    Label(model_frame, text="Language:", font=consolas_font).pack(side='left', padx=10)
    app.language_var = StringVar(master)
    app.language_var.set("Select Language")
    app.language_dropdown = OptionMenu(model_frame, app.language_var, "C#", "C", "C++", "Python", "Java", "JavaScript")
    app.language_dropdown.config(font=consolas_font)
    app.language_dropdown.pack(side='left')

    # LLM status on the same line
    status_frame = Frame(master)
    status_frame.pack(fill='x')
    Button(status_frame, text="Check LLM Status", command=app.check_llm_status, font=consolas_font).pack(side='left', padx=10)
    app.llm_status_label = Label(status_frame, text="LLM Status: Unknown", font=consolas_font)
    app.llm_status_label.pack(side='left', padx=20)

    # Output Text Box with Scrollbar
    app.text_box = Text(master, wrap='word', height=8, font=consolas_font)
    app.text_box.pack(fill='both', expand=True)
    scroll_y = Scrollbar(app.text_box, command=app.text_box.yview)
    app.text_box.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side='right', fill='y')

    # Move the Exit button to the bottom right of the window below the output text box
    bottom_frame = Frame(master)
    bottom_frame.pack(fill='x', side='bottom', pady=10)
    Button(bottom_frame, text="Exit", command=master.quit, font=consolas_font).pack(side='right', padx=10)

    # Center the main window on the screen
    master.update_idletasks()
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    window_width = master.winfo_width()
    window_height = master.winfo_height()
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    master.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Add a DEBUG flag to log window size adjustments
    RESIZE_DEBUG = False

    def on_resize(event):
        if RESIZE_DEBUG:
            new_size = f"Width: {event.width}, Height: {event.height}"
            app.text_box.insert(END, f"\nWindow resized: {new_size}\n")

    master.bind("<Configure>", on_resize)

    print("GUI layout setup complete.")  # Debug: Log GUI setup success

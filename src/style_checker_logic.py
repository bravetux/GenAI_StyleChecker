import os
import time
import threading
from tkinter import messagebox, END
from ollama_client import OllamaClient

def scan_files(folder_path, text_box):
    """
    Scans the provided folder path for .cs files and updates the GUI text box.

    Scans the provided folder path for .cs files and updates the GUI text box
    with a list of the found files. If the folder path is invalid or no .cs
    files are found, the GUI text box is updated with a relevant warning message.
    """

    # Delete any existing text in the text box
    text_box.delete(1.0, END)

    # Normalize the folder path to remove any trailing slashes
    folder_path = os.path.normpath(folder_path)

    # Check if the folder path is valid
    if not folder_path or not os.path.isdir(folder_path):
        # If the folder path is invalid, show a warning message
        messagebox.showwarning("Warning", "Invalid folder path.")
        return

    # Get a list of .cs files in the folder
    cs_files = [f for f in os.listdir(folder_path) if f.endswith('.cs')]

    # If no .cs files are found, update the text box with a warning message
    if not cs_files:
        text_box.insert(END, "No C# files found in the selected folder.\n")
        return

    # Insert a header line into the text box
    text_box.insert(END, "C# files found:\n")

    # Insert a line for each .cs file found
    for file in cs_files:
        text_box.insert(END, f"- {file}\n")

    # Move the text box to the end of the inserted text
    text_box.see(END)

def check_style(folder_path, model_var, text_box, threadsafe_gui_callback):
    """
    Initiates a background thread to check and correct the style of Language files.

    :param folder_path: The path to the folder containing C# files to be checked.
    :param model_var: A variable representing the selected model for style checking.
    :param text_box: The GUI text box where messages and updates will be displayed.
    :param threadsafe_gui_callback: A callback function to update the GUI in a thread-safe manner.
    """

    # Create a new thread to run the style checking process in the background.
    # This allows the GUI to remain responsive while the style check is being performed.
    thread = threading.Thread(
        target=_style_check_worker,  # The function to be executed in the new thread.
        args=(folder_path, model_var, text_box, threadsafe_gui_callback),  # Arguments to pass to the function.
        daemon=True  # Set the thread as a daemon so it will close when the main program exits.
    )

    # Start the execution of the thread. The _style_check_worker function will now
    # run in the background, processing each C# file and updating the GUI accordingly.
    thread.start()

def _style_check_worker(folder_path, model_var, text_box, gui_callback):
    """
    Worker thread that processes each C# file using the selected LLM model and style guide.
    This function is executed in a separate thread to avoid blocking the main program.
    """

    # Check if the folder path is valid
    if not folder_path:
        # If the folder path is invalid, show a warning message
        gui_callback(
            lambda: messagebox.showwarning(
                "Warning", "Please select a folder first."
            )
        )
        return

    # Read the C# style guide from the predefined location
    style_guide = _read_style_guide(gui_callback, text_box)
    if style_guide is None:
        # If there was an error reading the style guide, don't continue
        return

    # Get a list of .cs files in the folder path
    cs_files = [f for f in os.listdir(folder_path) if f.endswith('.cs')]

    # Check if any .cs files were found
    if not cs_files:
        # If no .cs files were found, show a warning message
        gui_callback(
            lambda: text_box.insert(
                END, "No C# files found in the selected folder.\n"
            )
        )
        return

    # Create a client to interact with the LLM
    ollama = OllamaClient()

    # Process each .cs file found
    for file in cs_files:
        _process_file(
            file, folder_path, style_guide, ollama, model_var, text_box, gui_callback
        )

    # Insert a message into the text box to indicate that all files have been processed
    gui_callback(
        lambda: text_box.insert(
            END, "\nAll files processed.\n"
        )
    )

    # Move the text box to the end of the inserted text
    gui_callback(
        lambda: text_box.see(END)
    )

def _read_style_guide(gui_callback, text_box):
    """
    Reads the C# style guide from the predefined location.

    :param gui_callback: A function to safely update the GUI from a different thread.
    :param text_box: The GUI text box widget where messages and errors will be displayed.
    :return: The contents of the style guide file as a string, or None if an error occurs.
    """
    
    # Construct the path to the style guide file by combining the directory of this script
    # with the relative path to the style guide file. This ensures that the path is correct
    # regardless of the environment in which the script is run.
    style_guide_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'style_guides', 'google_csharp_style_guide.txt')
    )

    try:
        # Attempt to open the style guide file in read mode.
        with open(style_guide_path, 'r') as sg_file:
            # Read the entire contents of the file and return it as a string.
            return sg_file.read()
    except Exception as e:
        # If an error occurs while opening or reading the file, update the GUI text box
        # with the error message. The gui_callback function ensures that this update is
        # performed safely from the GUI thread, avoiding any concurrency issues.
        gui_callback(lambda: text_box.insert(END, f"Error reading style guide: {e}\n"))
        
        # Return None to indicate that an error occurred and the style guide could not be read.
        return None

def _process_file(file, folder_path, style_guide, ollama, model_var, text_box, _threadsafe_gui):
    """
    This function is responsible for processing a single source code file using the selected Ollama model and the given style guide.
    It takes the following parameters:
        - file: The relative path to the source code file to process.
        - folder_path: The absolute path to the folder containing the source code file.
        - style_guide: The contents of the style guide file as a string.
        - ollama: An OllamaClient object which is used to send requests to the Ollama server.
        - model_var: A Tkinter StringVar object which contains the name of the currently selected Ollama model.
        - text_box: The GUI text box widget where messages and errors will be displayed.
        - _threadsafe_gui: A function to safely update the GUI from a different thread.

    The function writes the style guide and the source code to a .prompt file, sends the prompt to the Ollama server using the selected model,
    and writes the response to a .cs_mod file in the same directory as the source code file.
    """

    file_path = os.path.normpath(os.path.join(folder_path, file))
    selected_model = model_var.get()
    _threadsafe_gui(lambda: text_box.insert(END, f"Processing {file} with model '{selected_model}'...\n"))

    try:
        # Read the source code file
        with open(file_path, 'r', encoding='utf-8') as cf:
            code = cf.read()

        # Construct the prompt to send to the Ollama server
        prompt = (
            f"Check and rewrite the following C# code according to this style guide.\n"
            f"Style Guide:\n{style_guide}\n\n"
            f"Code:\n{code}\n\n"
            f"Return only the corrected code."
        )

        # Write the prompt to a .prompt file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prompt_file = os.path.normpath(os.path.join(folder_path, f"{os.path.splitext(file)[0]}_{timestamp}.cs_prompt"))
        _threadsafe_gui(lambda: text_box.insert(END, f"\n Creating Prompt file: {prompt_file} \n"))
        with open(prompt_file, 'w', encoding='utf-8') as pf:
            pf.write(prompt)

        # Send the prompt to the Ollama server and get the response
        start_time = time.time()
        response = ollama.send_request(prompt, model=selected_model)
        elapsed = time.time() - start_time

        if response:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            mod_file = os.path.normpath(os.path.join(folder_path, f"{os.path.splitext(file)[0]}_{timestamp}.cs_mod"))

            # Write the response from the Ollama server to a .cs_mod file
            with open(mod_file, 'w', encoding='utf-8') as mf:
                mf.write(response)

            _threadsafe_gui(lambda: text_box.insert(END, f"Processed {file} -> {mod_file} (in {elapsed:.2f}s)\n"))
        else:
            _threadsafe_gui(lambda: text_box.insert(END, f"No response from model for {file}.\n"))

    except Exception as e:
        _threadsafe_gui(lambda: text_box.insert(END, f"Error processing {file}: {e}\n"))


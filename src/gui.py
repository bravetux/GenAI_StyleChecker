from tkinter import Tk, filedialog, messagebox, END, Button
from gui_layout import setup_gui
from style_checker_logic import scan_files, check_style
from gui_utils import threadsafe_gui
import os
import requests
import datetime
import time

class StyleCheckerApp:
    def __init__(self, master):
        """
        Initializes the StyleCheckerApp window.
        
        :param master: The Tkinter root window.
        """
        print("Initializing StyleCheckerApp...")

        self.master = master
        master.title("C# Style Checker")
        master.geometry("1100x700")

        # Initialize instance variables
        self.folder_path = ''  # Stores the path to the folder containing C# files to check
        self.last_llm_response = None  # Stores the last response from the LLM
        self.last_llm_model = None  # Stores the name of the last LLM model used

        # Stores a mapping of language names to their corresponding file extensions
        self.language_extensions = {
            "C#": "cs",
            "C": "c",
            "C++": "cpp",
            "Python": "py",
            "Java": "java",
            "JavaScript": "js"
        }

        # Sets up the GUI layout
        setup_gui(master, self)

        # Updates the model dropdown list with the running LLM models
        self.update_model_list()

        # Checks the status of the LLM and updates the label accordingly
        self.check_llm_status()

        print("StyleCheckerApp initialized successfully.")

    def select_folder(self):
        """
        Opens a file dialog to select a folder containing C# files to check.

        This function is called when the user clicks the "Select Folder" button in the GUI.
        It opens a file dialog for the user to select a folder containing C# files to check.
        The selected folder path is stored in the instance variable self.folder_path and
        displayed in the folder path text box.

        :return: None
        """
        # Opens a file dialog to select a folder
        # This will open a file dialog window that allows the user to select a folder
        # containing C# files to check.
        folder_path = filedialog.askdirectory()

        # If the user selects a folder, store the selected folder path in the instance variable
        # self.folder_path.
        if folder_path:
            # Normalize the folder path to remove any trailing slashes
            # This is done to ensure the folder path is in a consistent format
            # regardless of how the user selected the folder (e.g. using the
            # file dialog, pasting the path, or typing it in manually)
            # The os.path.normpath function is used to normalize the folder path.
            self.folder_path = os.path.normpath(folder_path)

            # Clear the current folder path in the text box and insert the selected folder path
            # This updates the text box to display the selected folder path.
            # The self.folder_entry widget is the text box where the folder path is displayed.
            # The delete method is used to clear the current contents of the text box.
            # The insert method is used to insert the selected folder path into the text box.
            self.folder_entry.delete(0, END)
            self.folder_entry.insert(0, self.folder_path)

    def scan_files(self):
        # Retrieve the folder path from the input field
        # This is the path that the user has selected as the root directory
        # to search for files that match the criteria.
        folder_path = self.folder_entry.get()

        # Check if the folder path is empty and display an error if so
        # If the folder path is empty, it means the user hasn't selected
        # a directory to scan, so we display an error message to
        # inform the user.
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder to scan.")
            return

        # Get the selected programming language from a dropdown or similar UI element
        # This is the language that the user has selected as the language
        # for which they want to scan for files.
        selected_language = self.language_var.get()

        # Validate if the selected language is supported by checking if its extension is listed
        # We check if the selected language is supported by checking if its
        # extension is listed in the dictionary self.language_extensions.
        # If it is not listed, we display an error message to inform the user.
        if selected_language not in self.language_extensions:
            messagebox.showerror("Error", "Please select a valid language.")
            return

        # Get the file extension associated with the selected language
        # We retrieve the file extension associated with the selected language
        # from the dictionary self.language_extensions.
        extension = self.language_extensions[selected_language]

        # Initialize a list to store paths of files that match the criteria
        # We initialize an empty list to store the paths of all files that
        # match the criteria (i.e. are written in the selected language).
        matching_files = []

        # Walk through the directory structure starting from the selected folder path
        # We use os.walk to traverse the directory structure starting from the
        # selected folder path. os.walk yields a tuple containing the current
        # directory, the subdirectories within the current directory, and the
        # files within the current directory.
        for root, _, files in os.walk(folder_path):
            # Iterate over each file found in the current directory
            # We iterate over each file found in the current directory.
            for file in files:
                # Check if the file ends with the desired extension for the selected language
                # We check if the file ends with the desired extension for the
                # selected language. If it does, we add the full path of the
                # file to the list of matching files.
                if file.endswith(f".{extension}"):
                    # Add the full path of the matching file to the list
                    # We use os.path.join to join the root directory with the
                    # file name to form the full path of the matching file.
                    matching_files.append(os.path.join(root, file))

        # If no matching files are found, inform the user
        # If no files matching the criteria are found, we display an
        # informational message to inform the user.
        if not matching_files:
            messagebox.showinfo("Info", "No matching files found.")
        else:
            # If matching files are found, clear the text box and display the list of files
            # If files matching the criteria are found, we clear the text box
            # and display the list of matching files.
            self.text_box.delete(1.0, END)
            self.text_box.insert(END, "\n".join(matching_files))

    def check_style(self):
        # Removed the line that clears the output text box
        check_style(self.folder_entry.get().strip(), self.model_var, self.text_box, lambda func: threadsafe_gui(self.master, func))

    def update_model_list(self):
        """
        Queries the Ollama API to find the names of all running models,
        then updates the GUI dropdown list with the names of the running models.
        If there are no running models, the dropdown list will be empty and the
        model variable will be set to "No models running".
        If there is an error querying the Ollama API, the dropdown list will be
        empty and the model variable will be set to "Error fetching models".
        """
        try:
            # Queries the Ollama API to find the names of all running models
            # The response will be a JSON object containing a list of dictionaries,
            # where each dictionary represents a running model and has a 'name'
            # key with the name of the model as its value.
            response = requests.get("http://localhost:11434/api/ps", timeout=5)
            response.raise_for_status()
            data = response.json()

            # Extract the list of running models from the response
            running_models = data.get("models", [])

            # Clear the current contents of the dropdown list
            self.model_dropdown['menu'].delete(0, 'end')

            # If there are running models, populate the dropdown list with their names
            if running_models:
                # Iterate over the running models and add each one to the dropdown list
                # The 'label' parameter is the text that will be displayed in the dropdown list
                # The 'command' parameter is a callable that will be executed when the item is selected
                # We use a lambda function to capture the value of the model name and set it as the
                # value of the model variable when the item is selected.
                for model_info in running_models:
                    model_name = model_info.get('name', 'Unknown')
                    self.model_dropdown['menu'].add_command(
                        label=model_name,
                        command=lambda value=model_name: self.model_var.set(value)
                    )

                # Set the value of the model variable to the name of the first running model
                # If there are no running models, the model variable will be set to "No models running"
                self.model_var.set(running_models[0].get('name', 'Unknown'))
            else:
                # If there are no running models, set the value of the model variable to "No models running"
                self.model_var.set("No models running")
        except requests.exceptions.RequestException as e:
            # If there is an error querying the Ollama API, set the value of the model variable to
            # "Error fetching models" and print an error message
            print(f"Error fetching Ollama models: {e}")
            self.model_var.set("Error fetching models")

    def check_llm_status(self):
        """
        Periodically checks if the Ollama Server is running.

        The Ollama Server status is checked by sending a GET request to the Ollama Server API
        at http://localhost:11434/api/tags. If the request succeeds (with a
        status code of 200), the Ollama Server is considered to be running and the
        Ollama Server status label is set to "Ollama Status: Running" with a green color.
        If the request fails (with any other status code), or if any other
        exception occurs while sending the request, the Ollama Server is considered
        to be stopped and the Ollama Server status label is set to "Ollama Status: Stopped"
        with a red color.
        """
        try:
            # Send a GET request to the LLM API to check if the LLM is running
            response = requests.get("http://localhost:11434/api/tags", timeout=2)

            # If the request succeeds, the LLM is running
            if response.status_code == 200:
                # Set the LLM status label to "Ollama Server: Running" with a green color
                self.llm_status_label.config(text="Ollama Server: Running", fg="green")
            else:
                # If the request fails, the LLM is stopped
                # Set the LLM status label to "Ollama Server: Stopped" with a red color
                self.llm_status_label.config(text="Ollama Server: Stopped", fg="red")
        except Exception:
            # If any exception occurs while sending the request, the LLM is stopped
            # Set the LLM status label to Ollama Server: Stopped" with a red color
            self.llm_status_label.config(text="Ollama Server: Stopped", fg="red")

def _process_file(self, file, style_guide, ollama):
    """
    Process a single source file using the selected Ollama model and the given style guide.
    Writes the reformatted code to a timestamped _mod file and saves the prompt used.
    """
    try:
        # Resolve input and output paths
        # Normalize the input file path by combining the base folder path with the file name
        input_path = os.path.normpath(os.path.join(self.folder_path, file))
        
        # Get and normalize the output folder path from the GUI entry
        output_folder = os.path.normpath(self.output_folder_entry.get())

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        # Retrieve the selected model from the GUI component
        selected_model = self.model_var.get()

        # Generate a timestamp for file naming
        timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        
        # Extract the base file name and extension
        file_name, file_ext = os.path.splitext(file)

        # Construct output filenames with the timestamp
        mod_filename = f"{file_name}_{timestamp}_mod{file_ext}"
        prompt_filename = f"{file_name}_{timestamp}_mod.prompt"

        # Complete paths for the output files
        mod_path = os.path.join(output_folder, mod_filename)
        prompt_path = os.path.join(output_folder, prompt_filename)

        # Log the start of processing to the GUI
        self._threadsafe_gui(lambda: self.text_box.insert(END, f"\n\nProcessing {file} with model '{selected_model}'...\n"))

        # Read the input source code from the file
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Construct the prompt to be sent to the LLM
        prompt = (
            f"Check and rewrite the following C# code according to this style guide.\n"
            f"Style Guide:\n{style_guide}\n\n"
            f"Code:\n{code}\n\n"
            f"Return only the corrected code."
        )

        # Debug: print prompt and model info
        print(f"Sending to Ollama model: {selected_model}")
        print(f"Prompt:\n{prompt}\n")

        # Measure time taken for LLM response
        start_time = time.time()
        response = ollama.send_request(prompt, model=selected_model)
        elapsed = time.time() - start_time

        # If no response, log the issue to GUI and exit
        if not response:
            self._threadsafe_gui(lambda: self.text_box.insert(END, f"No response from model for {file}.\n"))
            return

        # Write the modified code to the output file
        with open(mod_path, 'w', encoding='utf-8') as out_file:
            out_file.write(response)

        # Save the prompt used to a file
        with open(prompt_path, 'w', encoding='utf-8') as pf:
            pf.write(prompt)

        # Save the last LLM response and model used for potential debugging or reference
        self.last_llm_response = response
        self.last_llm_model = selected_model

        # Log the successful processing and file details to the GUI
        self._threadsafe_gui(lambda: self.text_box.insert(END, f"Processed {file} -> {mod_path} (in {elapsed:.2f}s)\n"))
        self._threadsafe_gui(lambda: self.text_box.insert(END, f"Prompt written to: {prompt_path}\n"))

    except Exception as e:
        # Handle any exceptions that occur during processing
        error_msg = f"Error processing {file}: {e}"
        print(error_msg)
        self._threadsafe_gui(lambda: self.text_box.insert(END, error_msg + "\n"))

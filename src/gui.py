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
        print("Initializing StyleCheckerApp...")

        self.master = master
        master.title("C# Style Checker")
        master.geometry("1100x700")

        self.folder_path = ''
        self.last_llm_response = None
        self.last_llm_model = None

        self.language_extensions = {
            "C#": "cs",
            "C": "c",
            "C++": "cpp",
            "Python": "py",
            "Java": "java",
            "JavaScript": "js"
        }

        setup_gui(master, self)
        self.update_model_list()

        self.check_llm_status()
        print("StyleCheckerApp initialized successfully.")

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_path = os.path.normpath(self.folder_path)
            self.folder_entry.delete(0, END)
            self.folder_entry.insert(0, self.folder_path)

    def scan_files(self):
        folder_path = self.folder_entry.get()
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder to scan.")
            return

        selected_language = self.language_var.get()
        if selected_language not in self.language_extensions:
            messagebox.showerror("Error", "Please select a valid language.")
            return

        extension = self.language_extensions[selected_language]
        matching_files = []

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(f".{extension}"):
                    matching_files.append(os.path.join(root, file))

        if not matching_files:
            messagebox.showinfo("Info", "No matching files found.")
        else:
            self.text_box.delete(1.0, END)
            self.text_box.insert(END, "\n".join(matching_files))

    def check_style(self):
        # Removed the line that clears the output text box
        check_style(self.folder_entry.get().strip(), self.model_var, self.text_box, lambda func: threadsafe_gui(self.master, func))

    def update_model_list(self):
        try:
            response = requests.get("http://localhost:11434/api/ps", timeout=5)
            response.raise_for_status()
            data = response.json()
            print(f"Raw response from Ollama: {data}")

            running_models = data.get("models", [])

            self.model_dropdown['menu'].delete(0, 'end')

            if running_models:
                for model_info in running_models:
                    model_name = model_info.get('name', 'Unknown')
                    self.model_dropdown['menu'].add_command(
                        label=model_name,
                        command=lambda value=model_name: self.model_var.set(value)
                    )
                self.model_var.set(running_models[0].get('name', 'Unknown'))
            else:
                self.model_var.set("No models running")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Ollama models: {e}")
            self.model_var.set("Error fetching models")

    def check_llm_status(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                self.llm_status_label.config(text="LLM Status: Running", fg="green")
            else:
                self.llm_status_label.config(text="LLM Status: Stopped", fg="red")
        except Exception:
            self.llm_status_label.config(text="LLM Status: Stopped", fg="red")

def _process_file(self, file, style_guide, ollama):
    """
    Process a single source file using the selected Ollama model and the given style guide.
    Writes the reformatted code to a timestamped _mod file and saves the prompt used.
    """
    try:
        # Resolve input and output paths
        input_path = os.path.normpath(os.path.join(self.folder_path, file))
        output_folder = os.path.normpath(self.output_folder_entry.get())

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        selected_model = self.model_var.get()
        timestamp = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
        file_name, file_ext = os.path.splitext(file)

        # Construct output filenames
        mod_filename = f"{file_name}_{timestamp}_mod{file_ext}"
        prompt_filename = f"{file_name}_{timestamp}_mod.prompt"

        mod_path = os.path.join(output_folder, mod_filename)
        prompt_path = os.path.join(output_folder, prompt_filename)

        self._threadsafe_gui(lambda: self.text_box.insert(END, f"\n\nProcessing {file} with model '{selected_model}'...\n"))

        # Read input code
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Construct prompt
        prompt = (
            f"Check and rewrite the following C# code according to this style guide.\n"
            f"Style Guide:\n{style_guide}\n\n"
            f"Code:\n{code}\n\n"
            f"Return only the corrected code."
        )

        # Debug: print prompt and start time
        print(f"Sending to Ollama model: {selected_model}")
        print(f"Prompt:\n{prompt}\n")

        start_time = time.time()
        response = ollama.send_request(prompt, model=selected_model)
        elapsed = time.time() - start_time

        # Handle response
        if not response:
            self._threadsafe_gui(lambda: self.text_box.insert(END, f"No response from model for {file}.\n"))
            return

        # Write modified code
        with open(mod_path, 'w', encoding='utf-8') as out_file:
            out_file.write(response)

        # Write prompt file
        with open(prompt_path, 'w', encoding='utf-8') as pf:
            pf.write(prompt)

        # Save LLM response state
        self.last_llm_response = response
        self.last_llm_model = selected_model

        # Log to GUI
        self._threadsafe_gui(lambda: self.text_box.insert(END, f"Processed {file} -> {mod_path} (in {elapsed:.2f}s)\n"))
        self._threadsafe_gui(lambda: self.text_box.insert(END, f"Prompt written to: {prompt_path}\n"))

    except Exception as e:
        error_msg = f"Error processing {file}: {e}"
        print(error_msg)
        self._threadsafe_gui(lambda: self.text_box.insert(END, error_msg + "\n"))

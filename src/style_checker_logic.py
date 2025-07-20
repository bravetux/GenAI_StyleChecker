import os
import time
import threading
from tkinter import messagebox, END
from ollama_client import OllamaClient

def scan_files(folder_path, text_box):
    """
    Scans the provided folder path for .cs files and updates the GUI text box.
    """
    text_box.delete(1.0, END)
    folder_path = os.path.normpath(folder_path)

    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showwarning("Warning", "Invalid folder path.")
        return

    cs_files = [f for f in os.listdir(folder_path) if f.endswith('.cs')]
    if not cs_files:
        text_box.insert(END, "No C# files found in the selected folder.\n")
        return

    text_box.insert(END, "C# files found:\n")
    for file in cs_files:
        text_box.insert(END, f"- {file}\n")
    text_box.see(END)

def check_style(folder_path, model_var, text_box, threadsafe_gui_callback):
    """
    Starts a background thread to check and correct style of C# files.
    """
    thread = threading.Thread(
        target=_style_check_worker,
        args=(folder_path, model_var, text_box, threadsafe_gui_callback),
        daemon=True
    )
    thread.start()

def _style_check_worker(folder_path, model_var, text_box, gui_callback):
    """
    Worker thread that processes each C# file using the selected LLM model and style guide.
    """
    if not folder_path:
        gui_callback(lambda: messagebox.showwarning("Warning", "Please select a folder first."))
        return

    style_guide = _read_style_guide(gui_callback, text_box)
    if style_guide is None:
        return

    cs_files = [f for f in os.listdir(folder_path) if f.endswith('.cs')]
    if not cs_files:
        gui_callback(lambda: text_box.insert(END, "No C# files found in the selected folder.\n"))
        return

    ollama = OllamaClient()
    for file in cs_files:
        _process_file(file, folder_path, style_guide, ollama, model_var, text_box, gui_callback)

    gui_callback(lambda: text_box.insert(END, "\nAll files processed.\n"))
    gui_callback(lambda: text_box.see(END))

def _read_style_guide(gui_callback, text_box):
    """
    Reads the C# style guide from the predefined location.
    """
    style_guide_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'style_guides', 'google_csharp_style_guide.txt')
    )
    try:
        with open(style_guide_path, 'r') as sg_file:
            return sg_file.read()
    except Exception as e:
        gui_callback(lambda: text_box.insert(END, f"Error reading style guide: {e}\n"))
        return None

# def _process_file(file, folder_path, style_guide, ollama, model_var, text_box, gui_callback):
#     """
#     Sends the file content to the LLM for style correction and writes back the response.
#     """
#     file_path = os.path.normpath(os.path.join(folder_path, file))
#     model = model_var.get()
#     gui_callback(lambda: text_box.insert(END, f"Processing {file} with model '{model}'...\n"))

#     try:
#         with open(file_path, 'r', encoding='utf-8') as code_file:
#             code_content = code_file.read()

#         prompt = (
#             f"Check and rewrite the following C# code according to this style guide.\n"
#             f"Style Guide:\n{style_guide}\n\n"
#             f"Code:\n{code_content}\n\n"
#             f"Return only the corrected code."
#         )

#         start_time = time.time()
#         response = ollama.send_request(prompt, model=model)
#         duration = time.time() - start_time

#         if response:
#             timestamp = time.strftime("%Y%m%d_%H%M%S")
#             mod_filename = f"{os.path.splitext(file)[0]}_{timestamp}.cs_mod"
#             mod_filepath = os.path.normpath(os.path.join(folder_path, mod_filename))

#             with open(mod_filepath, 'w', encoding='utf-8') as out_file:
#                 out_file.write(response)

#             gui_callback(lambda: text_box.insert(END, f"Processed {file} -> {mod_filepath} (in {duration:.2f}s)\n"))
#         else:
#             gui_callback(lambda: text_box.insert(END, f"No response from model for {file}.\n"))

#     except Exception as e:
#         gui_callback(lambda: text_box.insert(END, f"Error processing {file}: {e}\n"))

def _process_file(file, folder_path, style_guide, ollama, model_var, text_box, _threadsafe_gui):
    file_path = os.path.normpath(os.path.join(folder_path, file))
    selected_model = model_var.get()
    _threadsafe_gui(lambda: text_box.insert(END, f"Processing {file} with model '{selected_model}'...\n"))

    try:
        with open(file_path, 'r', encoding='utf-8') as cf:
            code = cf.read()

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

        start_time = time.time()
        response = ollama.send_request(prompt, model=selected_model)
        elapsed = time.time() - start_time

        if response:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            mod_file = os.path.normpath(os.path.join(folder_path, f"{os.path.splitext(file)[0]}_{timestamp}.cs_mod"))

            with open(mod_file, 'w', encoding='utf-8') as mf:
                mf.write(response)

            _threadsafe_gui(lambda: text_box.insert(END, f"Processed {file} -> {mod_file} (in {elapsed:.2f}s)\n"))
        else:
            _threadsafe_gui(lambda: text_box.insert(END, f"No response from model for {file}.\n"))

    except Exception as e:
        _threadsafe_gui(lambda: text_box.insert(END, f"Error processing {file}: {e}\n"))


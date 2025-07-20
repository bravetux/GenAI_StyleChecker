# GENAI Language Style Checker

This project is a Language style checker that verifies language files against the Google Lanuage Style Guide. It provides a graphical user interface (GUI) for ease of use and integrates with the Ollama Llama3 API for enhanced functionality.

## Project Structure

```
GenAI_StyleChecker
├── src
│   ├── main.py           # Entry point of the application
│   ├── gui.py            # GUI implementation
|   ├── gui_layout.py     # GUI Main Window Layout
|   ├── gui_utils.py      # Thread Safe GUI
│   ├── style_checker.py  # Style checking logic
│   ├── ollama_client.py  # Interaction with Ollama Llama3 API
│   └── utils.py          # Utility functions for file operations
├── style_guides
│   └── google_csharp_style_guide.txt  # Google C# Style Guide
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd GenAI_StyleChecker
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Execute the following command to start the application:
   ```
   python src/main.py
   ```

## Usage Guidelines

- Use the "Select Folder" button to choose a directory containing C# files.
- Click the "Scan" button to check the selected C# files against the Google C# Style Guide.
- The modified files will be saved with the `.cs_mod` extension in the same directory as the original files.
- Use the "Exit" button to close the application.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

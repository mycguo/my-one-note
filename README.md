# My OneNote - Microsoft OneNote Clone

A Microsoft OneNote clone built with Streamlit, featuring a hierarchical organization system with Notebooks, Sections, and Pages.

## Features

- 📚 **Notebooks**: Create and manage multiple notebooks
- 📑 **Sections**: Organize content within notebooks using sections
- 📄 **Pages**: Create multiple pages within each section
- ✏️ **Markdown Support**: Write formatted content using Markdown syntax
- 💾 **Auto-save**: Content is automatically saved as you type
- 🎨 **Clean UI**: Intuitive sidebar navigation and main content area

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd my-one-note
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. The application will open in your default web browser.

3. **Getting Started:**
   - Create a new notebook using the sidebar
   - Add sections to organize your notes
   - Create pages within sections
   - Start writing your notes with Markdown support!

## Project Structure

```
my-one-note/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # Data storage directory (created automatically)
    └── notebooks.json # Notebooks data storage
```

## Data Storage

All notebooks, sections, and pages are stored in JSON format in the `data/notebooks.json` file. The data persists between sessions.

## Technologies Used

- **Streamlit**: Web framework for building the application
- **Python**: Backend logic and data management
- **JSON**: Data persistence

## License

This project is open source and available for personal use.
# Note

Performance may vary upon device used to run the program as the software for removing the background is quite process heavy

# Fitgen

This project allows users to upload photos of their clothing items and categorizes them as tops, bottoms, or shoes. Users can then click a "Randomize" button to generate a random outfit consisting of a top, bottom, and shoes.

## How to Use

1. Clone the repository.
2. Install the required dependencies.
3. Use the GUI to upload images of clothing items, remove backgrounds, categorize them, and randomize outfits.

## Installation

### 1. Install Python

Ensure you have Python installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).

### 2. Install `Tkinter`

`Tkinter` is a built-in Python GUI library, but it may need to be installed depending on your operating system. Follow the instructions below based on your OS.

#### macOS:

1. Install [Homebrew](https://brew.sh/) (if not installed):

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python 3 and `Tkinter` via Homebrew:
   ```bash
   brew install python-tk
   ```

#### Windows:

On Windows, `Tkinter` should come pre-installed with Python 3. However, if it's missing or causing issues:

1. Download and install the latest version of Python from [python.org](https://www.python.org/downloads/), ensuring that the **"Add Python to PATH"** option is checked during installation.
2. Verify that `Tkinter` is installed by running the following in Python:

   ```python
   import tkinter
   tkinter._test()
   ```

   If the test window opens, `Tkinter` is correctly installed.

#### Linux (Ubuntu/Debian-based):

1. Install `Tkinter` using the following command:

   ```bash
   sudo apt-get install python3-tk
   ```

2. Verify the installation by running the following in Python:
   ```python
   import tkinter
   tkinter._test()
   ```

### 3. Install Required Python Packages

```bash
# if running on python 2.x
pip install -r requirements.txt
# if running on python 3.x
pip3 install -r requirements.txt
python randomizer.py
```

### Summary of the Files

1. **README.md**: Detailed instructions on the project usage, including installation, training, and running the GUI.
2. **requirements.txt**: Lists the dependencies required for the project.
3. **randomizer.py**: GUI application script to upload, process, categorize images, and randomize outfits.

### Example images

There are some images provided in exampleImages that a user can use to test the functionality of the program.

# Build & Deploy Instructions

## Install dependencies
pip install PySide6 pyinstaller

## Run in development
python main.py

## Build executable
pyinstaller --noconfirm --onefile --windowed main.py

## Output
- Find `.exe` in /dist folder

import sys
import os

# Menambahkan folder backend ke path agar import berfungsi dengan baik
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app

if __name__ == "__main__":
    app.run()

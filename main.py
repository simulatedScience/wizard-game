"""
This module starts the wizard game GUI as a new window.

last edited: 25.05.2022
author: Sebastian Jost
version 0.2
"""
import tkinter as tk
from program_files.menu_gui import Menu_Gui

def main():
    wizard_gui = Menu_Gui()
    tk.mainloop()

if __name__ == "__main__":
    main()
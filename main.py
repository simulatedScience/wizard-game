"""
This module starts the wizard game GUI as a new window.

last edited: 25.05.2022
author: Sebastian Jost
version 0.2
"""
import tkinter as tk
from program_files.wizard_menu_gui import Wizard_Menu_Gui

def main():
    wizard_gui = Wizard_Menu_Gui()
    tk.mainloop()

if __name__ == "__main__":
    main()
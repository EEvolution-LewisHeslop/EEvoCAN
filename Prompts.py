import tkinter as tk
from tkinter import filedialog

# Handles the resizing of the x and y values of the derate tables.
class Prompts():
    @classmethod
    def fileOpenPrompt(cls):
        root = tk.Tk()
        root.withdraw()
        return filedialog.askopenfilename()
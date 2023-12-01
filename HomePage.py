import customtkinter
import tkinter as tk
from responsiveimage import ResponsiveImage
from PIL import ImageTk, Image

# Creates the basic tab
class HomeTab(customtkinter.CTkFrame):
    background: str
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.background = self._bg_color
        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)

        # # Create the homepage logo.
        logoFp = "resources/EEvolution_Logo.png"
        logoImage = Image.open(logoFp)
        self.logoStretchy = ResponsiveImage(self, image=logoImage)
        self.logoStretchy.grid(row=0, column=0, sticky='nsew')
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

        # Create the homepage logo.
        logoFp = "resources/EEvolution_Logo.png"
        logoImage = Image.open(logoFp)
        self.logoStretchy = ResponsiveImage(self, image=logoImage)
        self.logoStretchy.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # Create about box.
        self.aboutBoxFrame = customtkinter.CTkFrame(self)
        self.aboutBoxFrame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.aboutBoxFrame.grid_columnconfigure(index=0, weight=1)
        versionNumber = "0.0.0.1"
        aboutText = (f"Welcome to EEvoCAN™, an all in one CAN device"
                     f" configuration, monitoring, and interfacing tool.    "
                     f" Version {versionNumber}.    "
                     f" Copyright © 2024 EEvolution Battery Systems.")
        self.aboutBoxText = customtkinter.CTkLabel(self.aboutBoxFrame, text=aboutText)
        self.aboutBoxText.grid(row=0, column=0, padx=20, pady=10)

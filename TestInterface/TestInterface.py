import customtkinter
from os import listdir
from os.path import isfile, join
from pathlib import Path
import json

# Creates the basic tab
class TestInterfaceTab(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.grid_rowconfigure(index=0, weight=0)
        self.grid_rowconfigure(index=1, weight=100)

        # Create a dropdown menu of available test interface types.
        self.interfacePath = "resources/testinterfaces"
        self.interfaceTypeFiles = [f for f in listdir(self.interfacePath) if isfile(join(self.interfacePath, f))]
        self.interfaceTypes = [Path(t).stem for t in self.interfaceTypeFiles]
        self.interfaceDropdown = customtkinter.CTkOptionMenu(self, values=self.interfaceTypes)
        self.interfaceDropdown.grid(row=0, column=0, padx=10, pady=10, sticky='nw')

        # Create the frame for the default interfaceType.
        if (len(self.interfaceTypeFiles) > 0):
            self.interfaceFrame = self.generate_interfaceFrame(Path(self.interfacePath).joinpath(self.interfaceTypeFiles[0]))
            self.interfaceFrame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

    # Creates a given frame from its interface file's JSON data.    
    def generate_interfaceFrame(self, interfaceFilePath):
        generatedFrame = customtkinter.CTkScrollableFrame(self)
        # Read the JSON data in the filepath.
        jsonFile = open(interfaceFilePath)
        jsonData = json.load(jsonFile)

        # For each element in the JSON, produce the appropriate UI element.
        pos = -1
        for element in jsonData:
            pos += 1

            # Check to see if this is a digital input.
            
            generatedElement = self.generate_element(generatedFrame, pos, element)
            
        return generatedFrame
    
    # Creates an element on the given row, on the given master, from the given data.
    def generate_element(self, master, pos, elementData):
        UIelement = customtkinter.CTkLabel(master, text=elementData)
        UIelement.grid(row=pos, column=0, padx=5, pady=(0,5))
        return UIelement
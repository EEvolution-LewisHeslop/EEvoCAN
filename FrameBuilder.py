import customtkinter

def tab_builder(parent:customtkinter.CTkTabview, title, tabContent:customtkinter.CTkFrame, hwManager=None, commandSystem=None):
    # Build the tab
    tab = parent.add(title)
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)

    # Build the content, content will either have just command system, or command system and hwManager, or neither.
    if (commandSystem is None and hwManager is None):
        content = tabContent(tab)
    elif(hwManager is None):
            content:customtkinter.CTkFrame = tabContent(tab, commandSystem)
    else:
        content:customtkinter.CTkFrame = tabContent(tab, hwManager, commandSystem)
    content.grid(row=0, column=0, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
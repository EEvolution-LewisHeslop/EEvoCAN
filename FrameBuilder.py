import customtkinter

def tab_builder(parent:customtkinter.CTkTabview, title, tabContent, hwManager=None):
    # Build the tab
    tab = parent.add(title)
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)

    # Build the content
    if (hwManager is None):
        content = tabContent(tab)
    else:
        content = tabContent(tab, hwManager)
    content.grid(row=0, column=0, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
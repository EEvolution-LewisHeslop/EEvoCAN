import customtkinter

def tab_builder(parent:customtkinter.CTkTabview, title, tabContent):
    # Build the tab
    tab = parent.add(title)
    tab.grid_columnconfigure(0, weight=1)
    tab.grid_rowconfigure(0, weight=1)

    # Build the content
    content = tabContent(tab)
    content.grid(row=0, column=0, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
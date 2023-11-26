import customtkinter
import platformdirs
import configparser
import time

userprefs = platformdirs.user_data_dir(appname=__name__, appauthor='EEvolution', version=None, roaming=False, ensure_exists=True) + "/userprefs.ini"
def save_window_state(app:customtkinter.CTk):
    # Record the position and size of the window
    while(True):
        time.sleep(5)
        try:  
            config = configparser.ConfigParser()
            config.read(userprefs)
            config['Window'] = {'geometry': app.geometry()}
            with open(userprefs, 'w') as configfile:  
                config.write(configfile)
        except Exception as e:
            # Failed to record the window location.
            print("Failed to save window location:", e)
            create_prefs()
# Loads a value from the userprefs.ini
def load_prefs(section, value):
    # Try to open the preferences.        
    try:
        config = configparser.ConfigParser()        
        if (config.read(userprefs)):
            # Update the screen location based on prefs
            return config[section][value]
        else:
            # Userprefs is empty.
            create_prefs()
    except Exception as e:
        print("Failed to load preferences:", e)
        create_prefs()
# Recreates the userprefs.ini
def create_prefs():      
    try:       
        print("Creating new userprefs.")
        newConfig = configparser.ConfigParser()
        newConfig['Window'] = {'geometry': "1200x600"}
        with open(userprefs, 'w') as configfile:
            newConfig.write(configfile)
    except Exception as e:
        print("Failed to create new userprefs.")
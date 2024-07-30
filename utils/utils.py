from playsound import playsound
import os

def play_sound(audio_file_path):
    playsound(audio_file_path)
    return

def check_folder():
    if os.path.exists("data"):
        folders = os.listdir("data")
        if folders:
            folders.sort()
            last_folder_number = int(folders[-1].split("_")[-1])
            return f"data_{last_folder_number+1:02d}"
        return "data_00"
    return None
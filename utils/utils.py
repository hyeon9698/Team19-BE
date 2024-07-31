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

def prepare_conversation_data(log_content):
    lines = log_content.strip().split("\n")
    conversation = []
    summaries = []

    for line in lines:
        order_str, content = line.split(": ", 1)
        order = int(order_str.split("_")[0])
        role = order_str.split("_")[1]

        if role == "summary":
            summaries.append({"order": order, "summary": content})
        else:
            conversation.append({"order": order, "role": role, "content": content})

    data = {
        "conversation": conversation,
        "summaries": summaries
    }

    return data

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    and processes log.txt files.
    """
    dir_structure = {}

    for dirpath, dirnames, filenames in os.walk(rootdir):
        if 'log.txt' in filenames:
            with open(os.path.join(dirpath, 'log.txt'), 'r', encoding='utf-8') as file:
                log_content = file.read()
                relative_path = os.path.relpath(dirpath, rootdir)
                folders = relative_path.split(os.sep)

                subdir = dir_structure
                for folder in folders:
                    if folder not in subdir:
                        subdir[folder] = {}
                    subdir = subdir[folder]

                subdir['log.txt'] = prepare_conversation_data(log_content)

    return dir_structure
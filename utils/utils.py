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
    short_summary = ""
    long_summary = ""
    recommend_questions_1 = ""
    recommend_questions_2 = ""
    big_tag_list = []
    small_tag_list = []
    date = ""

    for line in lines:
        if "short_summary" in line:
            short_summary = line.split(": ", 1)[1]
        elif "long_summary" in line:
            long_summary = line.split(": ", 1)[1]
        elif "recommend_questions_1" in line:
            recommend_questions_1 = line.split(": ", 1)[1]
        elif "recommend_questions_2" in line:
            recommend_questions_2 = line.split(": ", 1)[1]
        elif "big_tag" in line:
            big_tag_list = line.split(": ", 1)[1].split(", ")
        elif "small_tag" in line:
            small_tag_list = line.split(": ", 1)[1].split(", ")
        elif "date" in line:
            date = line.split(": ", 1)[1]
        else:
            order_role, content = line.split(": ", 1)
            order_str, role = order_role.split("_", 1)
            order = int(order_str)
            conversation.append({"order": order, "role": role, "content": content})

    data = {
        # "conversation": conversation,
        "short_summary": short_summary,
        "long_summary": long_summary,
        "recommend_questions_1": recommend_questions_1,
        "recommend_questions_2": recommend_questions_2,
        "big_tag": big_tag_list,
        "small_tag": small_tag_list,
        "date": date,
    }

    return data

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    and processes log.txt files.
    """
    dir_structure = {}

    def process_directory(directory, structure):
        for entry in os.listdir(directory):
            entry_path = os.path.join(directory, entry)
            if os.path.isdir(entry_path):
                structure[entry] = {}
                process_directory(entry_path, structure[entry])
            elif entry == 'log.txt':
                with open(entry_path, 'r', encoding='utf-8') as file:
                    log_content = file.read()
                    log_data = prepare_conversation_data(log_content)
                    structure.update(log_data)

    process_directory(rootdir, dir_structure)

    return dir_structure
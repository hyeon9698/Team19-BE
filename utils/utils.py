import os
import telegram # pip install python-telegram-bot==13.13
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from collections import Counter
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 38

def check_folder():
    if os.path.exists("data"):
        # get only folder not files
        folders = [f for f in os.listdir("data") if os.path.isdir(os.path.join("data", f))]
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
        for entry in sorted(os.listdir(directory), reverse=True):
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

def telegram_send_message(text):
    try:
        telegram_token = os.getenv("telegram_api")
        telegram_chat_id = os.getenv("telegram_chat_id")
        bot = telegram.Bot(token=telegram_token)
        bot.sendMessage(chat_id=telegram_chat_id, text=text)
    except:
        pass
    return

def telegram_send_image(image_path):
    try:
        telegram_token = os.getenv("telegram_api")
        telegram_chat_id = os.getenv("telegram_chat_id")
        bot = telegram.Bot(token=telegram_token)
        bot.send_photo(chat_id=telegram_chat_id, photo=open(image_path, 'rb'))
    except:
        pass

def plot_big_tag(data):
    try:
        # data = {
        #     'item1': {'big_tag': ['요리', '과학']},
        #     'item2': {'big_tag': ['공룡', '기타']},
        #     'item3': {'big_tag': ['요리', '과학', '요리']},
        #     # Add more items as needed
        # }
        # Extract all big tags from the data
        all_big_tags = [tag for entry in data.values() for tag in entry["big_tag"]]
        
        # Count the occurrences of each big tag
        tag_counts = Counter(all_big_tags)
        
        # Get the top 4 most common big tags
        top_tags = tag_counts.most_common(4)
        
        # Separate the tags and their counts for plotting
        tags, counts = zip(*top_tags)
        
        # Set font to Pretendard
        # rcParams['font.family'] = 'Pretendard'
        
        # Create the bar plot with a kids' theme
        plt.figure(figsize=(10, 8))
        bars = plt.bar(tags, counts, color=['#7B61FF', '#B6A5FF', '#D3CFFF', '#E0D7FF'])
        # plt.xlabel('오늘 하루 우리 아이의 관심 태그', fontsize=24, fontweight='bold')
        # plt.ylabel('개수', fontsize=20, fontweight='bold')
        # plt.title('아이의 관심 태그', fontsize=24, fontweight='bold')
        
        # Add some decoration
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=38, fontweight='bold')
        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        plt.yticks([])
        plt.xticks(fontsize=38, fontweight='bold')
        plt.grid(False)
        plt.gca().tick_params(axis='x', pad=15)
        # plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('./data/plot.png')
        # plt.show()
    except:
        pass

if __name__ == "__main__":
    plot_big_tag("data")
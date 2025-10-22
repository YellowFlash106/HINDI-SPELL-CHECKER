import re
from collections import Counter
import pickle
import os

def load_titles(file_path):
    titles = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('page_title'):   
                parts = line.split('\t')
                if len(parts) > 1:
                    title = parts[1]
                else:
                    title = parts[0]
                titles.append(title)
    return titles

def tokenize_titles(titles):
     
    words = []
    for title in titles:
        title = title.replace('_', ' ')
        title = re.sub(r'\([^)]*\)', '', title)
        tokens = re.findall(r'[\u0900-\u097F]+|[\w]+', title)
        tokens = [token for token in tokens if len(token) > 1 and not token.isdigit()]
        words.extend(tokens)
    return words

def add_common_words():
     
    common_hindi = [
        'मैं', 'तुम', 'तू', 'यह', 'वह', 'वे', 'हम', 'आप', 'मुझे', 'तुम्हें', 'हमें',
        'है', 'हैं', 'था', 'थी', 'थे', 'रहा', 'रही', 'रहे', 'करना', 'किया', 'करता', 'करेगा',
        'जा', 'जाना', 'गया', 'आना', 'आया', 'रखा', 'लेना', 'दिया', 'ले',
        'और', 'पर', 'से', 'तक', 'के', 'का', 'की', 'को', 'में', 'पर', 'लेकिन', 'यदि', 'क्योंकि',
        'क्या', 'कौन', 'कहाँ', 'कब', 'कैसे', 'कितना', 'कितने', 'कई', 'कुछ',
        'एक', 'दो', 'तीन', 'चार', 'पांच', 'छह', 'सात', 'आठ', 'नौ', 'दस',
        'आज', 'कल', 'परसों', 'सिर्फ', 'हमेशा', 'कभी', 'दिन', 'रात', 'संस', 'साल',
        'अच्छा', 'बुरा', 'बड़ा', 'छोटा', 'नया', 'पुराना', 'लंबा', 'छोटा', 'गर्म', 'ठंडा',
        'लाल', 'नीला', 'हरा', 'काला', 'सफेद', 'घर', 'स्कूल', 'किताब', 'कक्षा', 'दोस्त', 'माता', 'पिता',
    ]
    common_english = [
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'have', 'has', 'do', 'does'
    ]
    return common_hindi + common_english

def build_frequency_dict(words):
     
    freq_dict = Counter(words)
    
    common_words = add_common_words()
    for word in common_words:
        if word not in freq_dict:
            freq_dict[word] = 1000
        else:
            freq_dict[word] += 500
    
    return freq_dict

def save_index(freq_dict, file_path='index.pkl'):
    with open(file_path, 'wb') as f:
        pickle.dump(freq_dict, f)

def load_index(file_path='index.pkl'):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return {}

if __name__ == '__main__':
     
    import sys
    import glob

    found = glob.glob('*all-titles*') + glob.glob('**/*all-titles*', recursive=True)
    found = [f for f in sorted(set(found)) if os.path.isfile(f)]

    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        hi = [p for p in found if 'hiwiki' in os.path.basename(p).lower()]
        if hi:
            paths = hi
        elif found:
            paths = found
        else:
            print("No '*all-titles*' files found in workspace. Please provide path(s) to title file(s) as arguments.")
            print("Example: python data_loader.py hiwiki-latest-all-titles/hiwiki-latest-all-titles")
            sys.exit(1)

    all_titles = []
    for p in paths:
        if not os.path.exists(p):
            print(f"Warning: path not found, skipping: {p}")
            continue
        print(f"Loading titles from: {p}")
        all_titles.extend(load_titles(p))

    if not all_titles:
        print("No titles loaded. Exiting.")
        sys.exit(1)

    words = tokenize_titles(all_titles)
    freq_dict = build_frequency_dict(words)
    save_index(freq_dict)
    print(f"Index built with {len(freq_dict)} unique words.")
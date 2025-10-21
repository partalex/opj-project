import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def error(msg: str) -> None:
    print(f"\033[91m{msg}\033[0m")

def export(splited: list[str]) -> list[str, str]:
    try:
        return splited[1], splited[-1].strip()
    except IndexError:
        error(f"Line not in CoNLL format: {splited}")
        return "error", "O"

#Ovo zameniti posle za sve tekstove + napraviti funkciju za svaki tekst pojedinacno
def load_conll_data(path) -> list[list[int | str]]:
    result = []
    error_label_map = {
        'B-NAGTAG': 'O',
        'I-NAGTAG': 'O',
        'o': 'O',
        'B=ORG': 'B-ORG',
        '_   B-ORG': 'B-ORG',
        'B-ROG': 'B-ORG',
        '': 'O',
        'B=PER': 'B-PER',
        'B-period': 'B-PER',
        '_  B-LOC': 'B-LOC',
        'B-LOX': 'B-LOC',
        'И': 'O',
        'I_ORG': 'I-ORG',
        'I-ROG': 'I-ORG',
        'I-EPR': 'I-PER'
    }

    with open(path, encoding='utf-8') as file:
        sentence_index = 0
        token_info = []

        for line in file:
            # ignore comments
            if line.startswith('#'):
                continue

            # check is this new line
            if line == '\n':
                continue

            # process line
            splited = line.split('\t')
            splited = export(splited)
            label = error_label_map.get(splited[1], splited[1])
            token_info.append(label)
            
           
    return token_info

def load_domain_data(data, domain_labels):
    domain_data = {}
    for label in domain_labels:
        matching_keys = [key for key in data.keys() if label in key]
        all_tokens = []
        for key in matching_keys:
            all_tokens.extend(data[key])
        domain_data[label] = all_tokens
    return domain_data


def statistics_whole_data(data):
    ukupno_tokena = 0
    type_statistics = {}
    for values in data.values():
        ukupno_tokena += len(values)
        for label in values:
            type_statistics.setdefault(label, []).append(label)

    #cuvanje u fajl statistike
    with open('statistics.txt', 'a', encoding="utf-8") as f:
        f.write("Ukupan broj tokena : ") 
        f.write(str(ukupno_tokena))

        f.write('\n')
        f.write("Broj tokena po labelama: \n")
        f.write("B-PER: "+ str(len(type_statistics['B-PER'])) + '\n')
        f.write("I-PER: "+ str(len(type_statistics['I-PER'])) + '\n')
        f.write('\n')
        f.write("B-ORG: "+ str(len(type_statistics['B-ORG'])) + '\n')
        f.write("I-ORG: "+ str(len(type_statistics['I-ORG'])) + '\n')
        f.write('\n')
        f.write("B-LOC: "+ str(len(type_statistics['B-LOC'])) + '\n')
        f.write("I-LOC: "+ str(len(type_statistics['I-LOC'])) + '\n')
        f.write('\n')
        f.write("O: "+ str(len(type_statistics['O'])) + '\n')
        f.write('\n')
        f.write("\nProcenat pojavljivanja po labelama:\n")
        
        for key in type_statistics.keys():
            percent = (len(type_statistics[key])/ukupno_tokena) * 100
            f.write(f"{key}: {percent:.2f}%\n")

    labels_list = ['B-LOC','B-ORG','B-PER','I-LOC','I-ORG','I-PER','O']

    #plotovanje statistike
    numbers = []
    for label in labels_list:
        numbers.append(len(type_statistics[label]))
        
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c2f0c2'] 

    fig, ax = plt.subplots(figsize=(10, 15))
    wedges, texts = ax.pie(numbers, startangle=90, colors=colors[:len(labels_list)], textprops={'fontsize': 14})

    # Legend with label + count
    legend_labels = [f"{label} ({len(count)}) - {len(count)/ukupno_tokena * 100:.2f}%" for label, count in type_statistics.items()]
    ax.legend(wedges, legend_labels, title="Labels", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.title("Distribucija tokena po labelama")
    plt.show()
    return ukupno_tokena


def statistics_domain_data(data, labels_list, ukupno_tokena):
    #Plotovanje za sve na jednom
    domain_dict = {}
    
    for key in data.keys():
        label_domain_list = data[key]
        data_dict = {label: 0 for label in labels_list}
        for label in label_domain_list:
            if label == 'ORG':
                continue
            data_dict[label] = data_dict[label] + 1
        domain_dict[key] = data_dict


    #Upisivanje u .txt fajl
    with open('statistics.txt', 'a', encoding="utf-8") as f:
        #U okviru celog data seta svi domeni medjusobno----------------------------------------------------------
        f.write("Broj labela podeljenih po domenima u odnosu na ceo tekst: \n")
        for key, value in domain_dict.items():
            f.write(f"Domen {key} \n")
            ukupno = 0
            for key_1, value_1 in value.items():
                ukupno += value_1
                f.write(f"{key_1} - broj tokena: {value_1} ( {value_1/ukupno_tokena * 100:.2f}% )\n")
            f.write(f"Ukupno za {key} - broj tokena : {ukupno} ( {ukupno/ukupno_tokena * 100:.2f}% )\n")
            f.write("\n\n")

        #Za svaki domen pojedinacno-------------------------------------------------------------------------------
        f.write("Statistika zasebno za svaki domen posebno\n")
        for key, value in domain_dict.items():
            f.write(f"Domen {key} \n")
            ukupno = 0
            for key_1, value_1 in value.items():
                ukupno += value_1
            for key_1, value_1 in value.items():
                f.write(f"{key_1} - broj tokena: {value_1} ( {value_1/ukupno * 100:.2f}% )\n")
            f.write(f"Ukupno za {key} - broj tokena : {ukupno}\n")
            f.write("\n\n")

    #Plotovanje ovoga
    #U okviru celog data seta svi domeni medjusobno----------------------------------------------------------
    domains = list(domain_dict.keys())
    labels = labels_list
    values = np.array([[domain_dict[domain][label] for label in labels] for domain in domains])

    # Plot grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.15  # širina pojedinačnog bara
    x = np.arange(len(domains))  # pozicije za domene

    colors = plt.cm.tab20.colors  # 20 različitih boja

    for i, label in enumerate(labels):
        ax.bar(x + i*bar_width, values[:, i], width=bar_width, label=label, color=colors[i % len(colors)])

    # Dodavanje brojeva unutar barova
    for i in range(len(domains)):
        for j in range(len(labels)):
            count = values[i, j]
            if count > 0:
                ax.text(x[i] + j*bar_width, count + 2, str(count), ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x + bar_width*(len(labels)/2 - 0.5))
    ax.set_xticklabels(domains, rotation=30)
    ax.set_ylabel("Token count")
    ax.set_title("Token distribution per domain and label")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

    #Za procente
    # Izračunavanje procenata po domenima
    percentages = np.zeros_like(values, dtype=float)
    for i in range(len(domains)):
        total = np.sum(values[i, :])
        if total > 0:
            percentages[i, :] = values[i, :] / total * 100

    # Plot grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.12
    x = np.arange(len(domains))

    colors = plt.cm.tab20.colors

    for i, label in enumerate(labels):
        ax.bar(x + i*bar_width, values[:, i], width=bar_width, label=label, color=colors[i % len(colors)])

    # Dodavanje procenta iznad barova
    for i in range(len(domains)):
        for j in range(len(labels)):
            pct = percentages[i, j]
            if pct > 0:
                ax.text(x[i] + j*bar_width, values[i, j] + 2, f"{pct:.2f}%", ha='center', va='bottom', fontsize=8)

    ax.set_xticks(x + bar_width*(len(labels)/2 - 0.5))
    ax.set_xticklabels(domains, rotation=30)
    ax.set_ylabel("Token count")
    ax.set_title("Token distribution per domain and label (percentages)")
    ax.set_ylabel("")  # uklonjena y-osa
    ax.set_yticks([])  # uklanjanje tickova sa y-ose
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    #Za svaki domen pojedinacno-------------------------------------------------------------------------------

    for key, value in domain_dict.items():
        labels = list(value.keys())
        counts = list(value.values())
        ukupno = 0
        for i in counts:
            ukupno += i
        percent = [i/ukupno * 100 for i in counts]
        # Create bar chart
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, counts, color='skyblue')

        # Add counts on top of each bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 50, f"{height}", ha='center', va='bottom', fontsize=10)

        ax.set_title(f"Za domen {key}")
        ax.set_ylabel("Count")
        plt.show()

        # Crtaj bar chart
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, percent, color='skyblue')

        # Dodaj procente iznad bara
        for bar, p in zip(bars, percent):
            ax.text(
                bar.get_x() + bar.get_width()/2,  # horizontalno centrirano
                p + 0.5,  # malo iznad bara
                f"{p:.2f}%",  # formatiran procenat sa dve decimale
                ha='center',
                va='bottom',
                fontsize=10
            )

        ax.set_title("Procenat po labelama")
        ax.set_ylabel("Procenat (%)")
        plt.show()

    
    
if __name__ == "__main__":

    root_input_folder = "anotirani_tekstovi"
    file_data = {}
    for root, dirs, files in os.walk(root_input_folder):
        relative_path = os.path.relpath(root, root_input_folder)

        for filename in files:
            if filename.endswith(".txt"):
                file_input_path = os.path.join(root, filename)
                token_data = load_conll_data(file_input_path)
                file_data[filename] = token_data
                token_data = []
    
    domain_labels = ['film_pozoriste', 'knjizevni', 'muzika', 'novinski', 'pravno_administrativni', 'tviter' ]
    #podaci raspodeljeni u domene
    domain_data = load_domain_data(file_data, domain_labels)

    #statistika nad celim skupom
    ukupno_tokena = statistics_whole_data(file_data)

    #statistika nad svakim domenom - zajedno prikazano
    labels_list = ['B-LOC','B-ORG','B-PER','I-LOC','I-ORG','I-PER','O']
    statistics_domain_data(domain_data, labels_list, ukupno_tokena)

               
                
    




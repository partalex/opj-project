import os
import shutil
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from simpletransformers.ner import NERModel, NERArgs
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report

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
                sentence_index += 1
                continue

            # process line
            splited = line.split('\t')
            splited = export(splited)

            word = splited[0]
            label = error_label_map.get(splited[1], splited[1])

            token_info.append(sentence_index)
            token_info.append(word)
            token_info.append(label)
            result.append(token_info)
            token_info = []
           
    return result

def load_conll_data_word(file_input_path):
    result = []
    with open(file_input_path, encoding='utf-8') as file:
        for line in file:
            # ignore comments
            if line.startswith('# text = '):
                result.append(line.split("=")[1])
    return result

def evaluate_model(data, model):
    model_data = pd.DataFrame(
        data, columns=["sentence_id", "words", "labels"]
    )
    result, model_outputs, preds_list = model.eval_model(model_data)
    return result, model_outputs, preds_list

def plot_confusion_matrix(y_pred,y_true, labels_list):
    cm = confusion_matrix(y_true, y_pred, labels=labels_list)
    cm_df = pd.DataFrame(cm, index=labels_list, columns=labels_list)

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues")
    plt.title("NER Confusion Matrix")
    plt.ylabel("True Labels")
    plt.xlabel("Predicted Labels")
    plt.show()
    return cm_df

if __name__ == "__main__":

    root_input_folder = "../../faza-2/anotirani_tekstovi"
    data_corpus = []
    data_sentence_corpus = []
    #prikupljanje tokena iz svih fajlova
    sentence_ind = 0
    for root, dirs, files in os.walk(root_input_folder):
        relative_path = os.path.relpath(root, root_input_folder)
        for filename in files:
            if filename.endswith(".txt"):
                file_input_path = os.path.join(root, filename)
                
                conll_data = load_conll_data(file_input_path)
                words_data = load_conll_data_word(file_input_path)

                conll_data_new = [[sentence_ind, item[1], item[2]] for item in conll_data]
                data_corpus.extend(conll_data_new)
                data_sentence_corpus.extend(words_data)
                sentence_ind += 1

    model_args = NERArgs()
    model_args.labels_list = ['B-LOC','B-MISC','B-ORG','B-PER','I-LOC','I-MISC','I-ORG','I-PER','O']
    model = NERModel(
        "electra", "classla/bcms-bertic-ner", args=model_args, use_cuda=False
    )
    predictions, raw_outputs = model.predict(data_sentence_corpus)
    y_true = []
    y_pred = []

    #isprintaj razlicite i nepostojane
    broj = 0
    for elem in predictions:
        for e in elem:
            word1 = data_corpus[broj][1]
            word2 = list(e.keys())[0]
            if word1 == word2 or word2.startswith(word1):
                y_true.append(data_corpus[broj][2])
                if e[word2] == 'B-MISC' or e[word2] == 'I-MISC':
                    y_pred.append('O')
                else:
                    y_pred.append(e[word2])
                broj+= 1
                continue
            
            while True:
                broj += 1
                word1 = data_corpus[broj][1]
                word2 = list(e.keys())[0]
                if word1 == word2 or word2.startswith(word1):
                    y_true.append(data_corpus[broj][2])
                    if e[word2] == 'B-MISC' or e[word2] == 'I-MISC':
                        y_pred.append('O')
                    else:
                        y_pred.append(e[word2])
                    broj+= 1
                    break
    
    #evaluacija modela sa prefiksima
    labels_list = ['B-LOC','B-ORG','B-PER','I-LOC','I-ORG','I-PER','O']
    scoring = {
        "accuracy" : accuracy_score(y_true, y_pred),
        "precision" : precision_score(y_true, y_pred, labels=labels_list, average=None),
        "recall" : recall_score(y_true, y_pred, labels=labels_list, average=None),
        "f1" : f1_score(y_true, y_pred, labels=labels_list, average=None)
    }
    plot_confusion_matrix(y_pred,y_true, model_args.labels_list)

    print("\nClassification report with prefixes B- and I-:")
    report = classification_report(y_true, y_pred, labels=labels_list, digits=4)
    print(report)
    with open("classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    #evaluacija modela bez prefiksa
    y_true_no_prefix = [label.split('-')[-1] if '-' in label else label for label in y_true]
    y_pred_no_prefix = [label.split('-')[-1] if '-' in label else label for label in y_pred]
    labels_list_no_prefix = ['LOC','ORG','PER','O']

    scoring_simple = {
        "accuracy" : accuracy_score(y_true_no_prefix, y_pred_no_prefix),
        "precision" : precision_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None),
        "recall" : recall_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None),
        "f1" : f1_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None)
    }
     
    print("\nClassification report without prefixes:")
    report = classification_report(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, digits=4)
    plot_confusion_matrix(y_pred_no_prefix,y_true_no_prefix, labels_list_no_prefix)
    with open("classification_report_no_prefix.txt", "w", encoding="utf-8") as f:
        f.write(report)


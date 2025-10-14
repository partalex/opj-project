import pandas as pd
from simpletransformers.ner import NERModel, NERArgs
import numpy as np
import os
import shutil
import matplotlib.pyplot as plt
import re
from transformers import pipeline
from sklearn.metrics import confusion_matrix
import seaborn as sns

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

            token_info.append(sentence_index)
            
            word = splited[0]
            label = splited[1]

            #provera
            if label == 'B-NAGTAG' or label == 'I-NAGTAG' or label == 'o':
                label = 'O'
            if label == 'B=ORG' or label == '_   B-ORG' or label == 'B-ROG':
                label = 'B-ORG'
            if label == '':
                label = 'O'
            if label == "B=PER" or label == "B-period":
                label = 'B-PER'
            if label == "_  B-LOC" or label == 'B-LOX':
                label = "B-LOC"
            if label == "И":
                label = "O"
            if label == 'I_ORG' or label == 'I-ROG':
                label = 'I-ORG'
            if label == 'I-EPR':
                label = 'I-PER'

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
                parts = line.split("=")
                result.append(parts[1])
    return result

#nad celim skupom podataka
def evaluate_whole_corpus_model(data, model):

    model_data = pd.DataFrame(
        data, columns=["sentence_id", "words", "labels"]
    )
    result, model_outputs, preds_list = model.eval_model(model_data)
    return result, model_outputs, preds_list

def plot_confusion_matrix(y_pred,y_true, labels_list):
    

    # Napravi matricu konfuzije
    cm = confusion_matrix(y_true, y_pred, labels=labels_list)
    cm_df = pd.DataFrame(cm, index=labels_list, columns=labels_list)

    # Prikaz sa heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues")
    plt.title("NER Confusion Matrix")
    plt.ylabel("True Labels")
    plt.xlabel("Predicted Labels")
    plt.show()

    return cm_df

if __name__ == "__main__":
    root_input_folder = "../../faza-2/anotirani_tekstovi"
    data_whole_corpus = []
    data_words_corpus = []
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
                data_whole_corpus.extend(conll_data_new)
                data_words_corpus.extend(words_data)
                sentence_ind += 1

    model_args = NERArgs()
    model_args.labels_list = ['B-LOC','B-MISC','B-ORG','B-PER','I-LOC','I-MISC','I-ORG','I-PER','O']
    model = NERModel(
        "electra", "classla/bcms-bertic-ner", args=model_args, use_cuda=False
    )

    predictions, raw_outputs = model.predict(data_words_corpus)
    y_true = []
    y_pred = []

    #isprintaj razlicite i nepostojane
    broj = 0
    for elem in predictions:
        for e in elem:
            word1 = data_whole_corpus[broj][1]
            word2 = list(e.keys())[0]
            if word1 == word2 or word2.startswith(word1):
                y_true.append(data_whole_corpus[broj][2])
                if e[word2] == 'B-MISC' or e[word2] == 'I-MISC':
                    y_pred.append('O')
                else:
                    y_pred.append(e[word2])
                broj+= 1
                continue
            
            while True:
                broj += 1
                word1 = data_whole_corpus[broj][1]
                word2 = list(e.keys())[0]
                if word1 == word2 or word2.startswith(word1):
                    y_true.append(data_whole_corpus[broj][2])
                    if e[word2] == 'B-MISC' or e[word2] == 'I-MISC':
                        y_pred.append('O')
                    else:
                        y_pred.append(e[word2])
                    broj+= 1
                    break

    for i, (s1, s2) in enumerate(zip(y_pred, y_true)):
        if s1 != s2:
            print(f"Razlika na indeksu {i}: '{s1}' != '{s2}'")

    plot_confusion_matrix(y_pred,y_true, model_args.labels_list)
    result, model_outputs, preds_list = model.eval_model(data_whole_corpus)
               
   
    


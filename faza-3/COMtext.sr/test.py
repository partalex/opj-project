import os
import sys
from glob import glob
import collections
import re
import torch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report


def map_labels(label):
    if label:
        if label == "B-ORGOTH" or label == "B-COMP":
            return "B-ORG"
        if label == "I-ORGOTH" or label == "I-COMP":
            return "I-ORG"
        if label == "B-PER":
            return "B-PER"
        if label == "I-PER":
            return "I-PER"
        if label == "B-TOP" or label =="B-ADR":
            return "B-LOC"
        if label == "I-TOP" or label =="I-ADR":
            return "I-LOC"
    return "O"

def process_file(file, ofile):
    ner_pipeline = pipeline(
        "ner",
        model="ICEF-NLP/bcms-bertic-comtext-sr-legal-ner-ekavica"
    )
    for line in file:

       
        if line and line[0].isdigit():
            currToken = line.strip().split('\t')[1]
            tokens.append(currToken)
            label = ner_pipeline(currToken)
           
            if label != []:
                labelmapped = map_labels(label[0]['entity'])
                parts = line.split('\t')
                parts[-1] = labelmapped
                newline = '\t'.join(parts)
                ofile.write(newline + '\n')
                
            else:
                ofile.write(line)

        else:
            ofile.write(line)

def collect_from_dir(directory):
        found = []
        for root, _, filenames in os.walk(directory):
            for fn in filenames:
                if fn.lower().endswith((".txt", ".conllu", ".conll")):
                    found.append(os.path.join(root, fn))
        return found

def compare_labels(file_name):
    y_true = []
    y_pred = []
    filep = open(file_name, encoding='utf-8')
    file_name = file_name.replace("faza-3\\COMtext.sr", "faza-2")
    file_name = file_name.replace("output_files", "anotirani_tekstovi")
    file_name = file_name.replace("tokenized_", "annotated_")
    file_name = file_name.replace(".pred.conllu", ".conllu") 
    filet = open(file_name, encoding='utf-8')
    for linep in filep:
        linet = filet.readline()
        if linep and linep[0].isdigit():
            partsp = linep.strip().split('\t')
            partst = linet.strip().split('\t')
            if len(partsp) < 2 or len(partst) < 2:
                continue
            y_true.append(partst[-1])
            y_pred.append(partsp[-1])
    
    filep.close()
    filet.close()
    return y_true, y_pred

def plot_confusion_matrix(y_pred,y_true, labels_list, prefixed, default_dir):
    cm = confusion_matrix(y_true, y_pred, labels=labels_list)
    cm_df = pd.DataFrame(cm, index=labels_list, columns=labels_list)

    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues")
    plt.title("NER Confusion Matrix")
    plt.ylabel("True Labels")
    plt.xlabel("Predicted Labels")
    
    if prefixed:
       
        img_path = os.path.join(default_dir, "confusion_matrix.prefixed.png")
    else:
        
        img_path = os.path.join(default_dir, "confusion_matrix.noprefixed.png")
    
    plt.savefig(img_path, bbox_inches="tight")

    return cm_df

if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_dir = default_dir = os.path.normpath(os.path.join(script_dir, "..", "..", "py-project", "tokenized_files"))

    tokens = []
    files = collect_from_dir(default_dir)
    print(f"Found {len(files)} files to process.")
    ner_pipeline = pipeline(
        "ner",
        model="ICEF-NLP/bcms-bertic-comtext-sr-legal-ner-ekavica"
    )
    labels = []
    y_true = []
    y_pred = []
    for (file_path) in files:
       # file = open(file_path, encoding='utf-8')
        file_path = file_path.replace("py-project", "faza-3\\COMtext.sr")
        file_path = file_path.replace("tokenized_files", "output_files")
        file_path = file_path.replace(".conllu", "")
        print(file_path)
        #ofile = open(file_path + ".pred.conllu", 'w', encoding='utf-8')
        #process_file(file, ofile)
        #file.close()
        #ofile.close()        
        yt, yp = compare_labels(file_path + ".pred.conllu")
        y_true.extend(yt)
        y_pred.extend(yp)   


    #evaluacija modela sa prefiksima
    labels_list = ['B-LOC','B-ORG','B-PER','I-LOC','I-ORG','I-PER','O']
    scoring = {
        "accuracy" : accuracy_score(y_true, y_pred),
        "precision" : precision_score(y_true, y_pred, labels=labels_list, average=None),
        "recall" : recall_score(y_true, y_pred, labels=labels_list, average=None),
        "f1" : f1_score(y_true, y_pred, labels=labels_list, average=None)
    }
    plot_confusion_matrix(y_pred,y_true, labels_list, True, default_dir)

    print("\nClassification report with prefixes B- and I-:")
    report = classification_report(y_true, y_pred, labels=labels_list, digits=4)
    print(report)
    with open("classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
        f.write("accuracy                         " +scoring["accuracy"].__str__())
        f.write("\n")

    print(scoring)
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
    print(scoring_simple)
    print("\nClassification report without prefixes:")
    report = classification_report(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, digits=4)
    plot_confusion_matrix(y_pred_no_prefix,y_true_no_prefix, labels_list_no_prefix, False, default_dir)
    with open("classification_report_no_prefix.txt", "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n")
        f.write("accuracy                         " +scoring["accuracy"].__str__())
        

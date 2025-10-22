from elg import Service
import os, glob
import seaborn as sns
from numpy.ma.core import append
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report
import pandas as pd
import matplotlib.pyplot as plt

service = Service.from_id(18077,local=True)
print(service)
# Service.scope="offline_access"

fix_label_map = {
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
        'I-PER': 'I-PER',
        'I-ORG': 'I-ORG',
        'I-LOC': 'I-LOC',
        'B-PER': 'B-PER',
        'B-ORG': 'B-ORG',
        'B-LOC': 'B-LOC',
        'O': 'O',
        'ORG': 'O',
        '0': 'O'
    }

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

def analizeFiles(file1, file2):
    # print(file1,file2)
    res=''
    seperatePerformacne = {}
    combinedPerformacne = {}
    missed = {}
    numOfAnn=0
    tagMap = {"PERS":["B-PER","I-PER"],"LOC":["B-LOC","I-LOC"],"ORG":["B-ORG","I-ORG"]}
    with open(file2,'r',encoding='utf-8') as file:
        line = file.readline()
        annFiles = dict()
        flen=0
        while(line):
            if(len(line)>2):
              if(line[0]!='#'):
                line = line.replace('\n', '')
                line = line.split('\t')
                if(line[0].isnumeric()):
                    if(line[-1]!='O'):
                        numOfAnn+=1
                    annFiles[flen]=[line[1],line[-1],'O']
                    if(line[-2]=="SpaceAfter=No"):
                        flen+=len(line[1])
                    else:
                        flen+=len(line[1])+1
            line= file.readline()
    # print(annFiles)
    with open(file1,'r',encoding='utf-8') as file:
        line = file.readline()
        while(line):
            if(line[0]!='#'):
                res+=line.replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')
            elif(line[:8]=='#text = '):
                res+=line[8:].replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')
            elif (line[:7] == '#text ='):
                res += line[7:].replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')
            line= file.readline()
    res=res.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace("Gvin18Kod", "GvinKod")
    # print(res)
    for each in annFiles.keys():
        if(annFiles[each][0]!=res[int(each):int(each)+len(annFiles[each][0])]):
            print("MISSMATCH")
        # print(annFiles[each][0])
        # print(res[int(each):int(each)+len(annFiles[each][0])])
    result = service(request_input=res, request_type="text", sync_mode=True)
    # print(result)
    result=result['annotations']
    # print(result)
    seperatePerformacne["pravno_administrativni_9.txt"]=0
    combinedPerformacne["pravno_administrativni_9.txt"]=0
    missed["pravno_administrativni_9.txt"]=0
    for key in set(['PERS','LOC','ORG']).intersection(result.keys()):
        # print(key+'\n')
        # print(result[key])
        for each in result[key]:
            if(each['start'] in annFiles.keys()):
                allMatches=list()
                for annFile in annFiles.keys():
                    if(annFile>=each['start'] and annFile<each['end']):
                        allMatches.append(annFile)
                        if(annFile!=each['start']):
                            annFiles[annFile][2]=tagMap[key][1]
                #             if(tagMap[key][1]==annFiles[annFile][1]):
                #                 combinedPerformacne["pravno_administrativni_9.txt"] += 1
                #             elif(tagMap[key][1]==annFiles[annFile][1]):
                #                 combinedPerformacne["pravno_administrativni_9.txt"] += 1
                #                 seperatePerformacne["pravno_administrativni_9.txt"] += 1
                #             else:
                #                 missed["pravno_administrativni_9.txt"] += 1
                # if(res[each['start']:each['end']]==annFiles[each['start']][0] and tagMap[key][0]==annFiles[each['start']][1]):
                #         seperatePerformacne["pravno_administrativni_9.txt"]+=1
                #         combinedPerformacne["pravno_administrativni_9.txt"] += 1
                # elif(res[each['start']:each['end']]==annFiles[each['start']][0] and tagMap[key][1]==annFiles[each['start']][1]):
                #         combinedPerformacne["pravno_administrativni_9.txt"] += 1
                # else:
                #     missed["pravno_administrativni_9.txt"] += 1

                annFiles[each['start']][2] = tagMap[key][0]
                # print('\t'+res[each['start']:each['end']], [annFiles[a] for a in allMatches])
            else:
                print('\t' + res[each['start']:each['end']], "FALI")

    # print("ANN FILES",annFiles)
    # print(set([annFiles[f][1] for f in annFiles.keys()]))
    trueCombo=[fix_label_map[annFiles[f][1]][2:] if len(annFiles[f][1])>1 else 'O' for f in annFiles.keys()]
    trueSep=[fix_label_map[annFiles[f][1]] for f in annFiles.keys()]
    predCombo=[fix_label_map[annFiles[f][2]][2:] if len(annFiles[f][2])>1 else 'O' for f in annFiles.keys()]
    predSep=[fix_label_map[annFiles[f][2]] for f in annFiles.keys()]
    # print(trueSep)
    # print(trueCombo)
    # print(predSep)
    # print(predCombo)
    # print("ACCURACY", accuracy_score(trueSep, predSep))
    # print("ACCURACY", accuracy_score(predCombo, trueCombo))
    # print("COMBO",len(annFiles.keys())-missed["pravno_administrativni_9.txt"])
    # print("SEPERATE",len(annFiles.keys())-missed["pravno_administrativni_9.txt"]+seperatePerformacne["pravno_administrativni_9.txt"]-combinedPerformacne["pravno_administrativni_9.txt"])
    seperatePerformacne["pravno_administrativni_9.txt"] = (len(annFiles.keys())-missed["pravno_administrativni_9.txt"]+seperatePerformacne["pravno_administrativni_9.txt"]-combinedPerformacne["pravno_administrativni_9.txt"])/(len(annFiles.keys()))
    #
    combinedPerformacne["pravno_administrativni_9.txt"] = (len(annFiles.keys())-missed["pravno_administrativni_9.txt"])/(len(annFiles.keys()))
    # print("COMBO",combinedPerformacne)
    # print("SEPERATE",seperatePerformacne)
    return (trueCombo,trueSep,predCombo,predSep)

pathText="..\\..\\faza-1\\Text fajlovi"
pathAnnot="..\\..\\faza-2\\anotirani_tekstovi"
matchedFiles=dict()
# print(glob.glob(os.path.join(pathText)))
for folder in glob.glob(os.path.join(pathText,"*")):
    for filename in glob.glob(os.path.join(folder, '*.txt')):
        # print(filename)
        # anFile=pathAnnot+'\\'+ folder.split('\\')[-1]+'\\'+'annotated_'+filename.split('\\')[-1]
        # print(anFile)
        matchedFiles[filename.split('\\')[-1]]=[filename]
    # with open(os.path.join(os.getcwd(), filename),

for folder in glob.glob(os.path.join(pathAnnot,"*")):
    for filename in glob.glob(os.path.join(folder, '*.txt')):
        # print(filename)
        # anFile=pathAnnot+'\\'+ folder.split('\\')[-1]+'\\'+'annotated_'+filename.split('\\')[-1]
        # print(anFile)
        matchedFiles[filename.split('\\')[-1][10:]].append(filename)
trueCombo,trueSep,predCombo,predSep=[],[],[],[]
for file in matchedFiles.keys():
    # print("POCINJE", matchedFiles[file][0])
    if(len(matchedFiles[file])<2):
        print("GRESKA",matchedFiles[file][0])
        continue
    prox1,prox2,prox3,prox4=analizeFiles(matchedFiles[file][0],matchedFiles[file][1])
    # analizeFiles(matchedFiles[file][0], matchedFiles[file][1])
    trueCombo=trueCombo+prox1
    trueSep=trueSep+prox2
    predCombo=predCombo+prox3
    predSep=predSep+prox4

# print("ACCURACY", accuracy_score(trueSep, predSep))
# print("ACCURACY", accuracy_score(predCombo, trueCombo))


labels_list = ['B-LOC', 'B-ORG', 'B-PER', 'I-LOC', 'I-ORG', 'I-PER', 'O']
scoring = {
    "accuracy": accuracy_score(trueSep, predSep),
    "precision": precision_score(trueSep, predSep, labels=labels_list, average=None),
    "recall": recall_score(trueSep, predSep, labels=labels_list, average=None),
    "f1": f1_score(trueSep, predSep, labels=labels_list, average=None)
}
plot_confusion_matrix(trueSep, predSep, labels_list)

print("\nClassification report with prefixes B- and I-:")
report = classification_report(trueSep, predSep, labels=labels_list, digits=4)
print(report)
with open("classification_report.txt", "w", encoding="utf-8") as f:
    f.write(report)

# evaluacija modela bez prefiksa
y_true_no_prefix = trueCombo
y_pred_no_prefix = predCombo
labels_list_no_prefix = ['LOC', 'ORG', 'PER', 'O']

scoring_simple = {
    "accuracy": accuracy_score(y_true_no_prefix, y_pred_no_prefix),
    "precision": precision_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None),
    "recall": recall_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None),
    "f1": f1_score(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, average=None)
}

print("\nClassification report without prefixes:")
report = classification_report(y_true_no_prefix, y_pred_no_prefix, labels=labels_list_no_prefix, digits=4)
plot_confusion_matrix(y_pred_no_prefix, y_true_no_prefix, labels_list_no_prefix)
# print(set(y_pred_no_prefix))
# print(y_true_no_prefix)
print(report)
with open("classification_report_no_prefix.txt", "w", encoding="utf-8") as f:
    f.write(report)
# print(trueCombo)
# print(trueSep)
# print(predCombo)
# print(predSep)
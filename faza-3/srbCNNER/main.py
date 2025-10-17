from elg import Service
import os, glob

from numpy.ma.core import append
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report

service = Service.from_id(18077,local=True)
print(service)
# Service.scope="offline_access"
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
    print(result)
    result=result['annotations']
    print(result)
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
                            if(tagMap[key][1]==annFiles[annFile][1]):
                                combinedPerformacne["pravno_administrativni_9.txt"] += 1
                            elif(tagMap[key][1]==annFiles[annFile][1]):
                                combinedPerformacne["pravno_administrativni_9.txt"] += 1
                                seperatePerformacne["pravno_administrativni_9.txt"] += 1
                            else:
                                missed["pravno_administrativni_9.txt"] += 1
                if(res[each['start']:each['end']]==annFiles[each['start']][0] and tagMap[key][0]==annFiles[each['start']][1]):
                        seperatePerformacne["pravno_administrativni_9.txt"]+=1
                        combinedPerformacne["pravno_administrativni_9.txt"] += 1
                elif(res[each['start']:each['end']]==annFiles[each['start']][0] and tagMap[key][1]==annFiles[each['start']][1]):
                        combinedPerformacne["pravno_administrativni_9.txt"] += 1
                else:
                    missed["pravno_administrativni_9.txt"] += 1

                annFiles[each['start']][2] = tagMap[key][0]
                # print('\t'+res[each['start']:each['end']], [annFiles[a] for a in allMatches])
            else:
                print('\t' + res[each['start']:each['end']], "FALI")

    # print("ANN FILES",annFiles)
    trueCombo=[annFiles[f][1][2:] if len(annFiles[f][1])>1 else 'O' for f in annFiles.keys()]
    trueSep=[annFiles[f][1] for f in annFiles.keys()]
    predCombo=[annFiles[f][2][2:] if len(annFiles[f][2])>1 else 'O' for f in annFiles.keys()]
    predSep=[annFiles[f][2] for f in annFiles.keys()]
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
print(glob.glob(os.path.join(pathText)))
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
    print("POCINJE", matchedFiles[file][0])
    if(len(matchedFiles[file])<2):
        print("GRESKA",matchedFiles[file][0])
        continue
    prox1,prox2,prox3,prox4=analizeFiles(matchedFiles[file][0],matchedFiles[file][1])
    # analizeFiles(matchedFiles[file][0], matchedFiles[file][1])
    trueCombo=trueCombo+prox1
    trueSep=trueSep+prox2
    predCombo=predCombo+prox3
    predSep=predSep+prox4

print("ACCURACY", accuracy_score(trueSep, predSep))
print("ACCURACY", accuracy_score(predCombo, trueCombo))


# print(trueCombo)
# print(trueSep)
# print(predCombo)
# print(predSep)
import os, glob
import itertools
path = 'toCompare'

linesStartAt=7

def compareTwo(filename, file1, file2):
    results = []
    tokens = 0
    annToken=0
    itterlen = min(len(file1),len(file2))
    for i in range(itterlen):
        if(file1[i] != '' and file1[i][0].isdigit()):
            tokens+=1
        if(len(file1[i].split('\t')[-1])<1 or len(file2[i].split('\t')[-1])<1):
            continue
        if(file1[i].split('\t')[-1][-1] != file2[i].split('\t')[-1][-1] or (file1[i].split('\t')[-1][-1]!='O' and (file1[i].split('\t')[-1][-5:]!= file2[i].split('\t')[-1][-5:])) ):
            # if(len(file1[i].split('\t')[-1])< and len(file1[i].split('\t')[-1])>1)
            print(file1[i].split('\t')[-1][-1] , file2[i].split('\t')[-1][-1])
            annToken+=1
            results.append("Razlika u fajlu url= "+filename+" na liniji: "+str(linesStartAt+i)+" (linije u pitanju: \""+file1[i]+"\" i \""+file2[i]+"\")")
        elif(file1[i] != '' and file1[i].split('\t')[-1][-1]!='O'):
            annToken+=1
        # elif (file2[i] != '' and file2[i].split('\t')[-1][-1] != 'O'):
        #     annToken += 1
        # else:
        #     annToken += 1
    return (tokens, annToken,results)

def compareAll(filename, files, whoseFile):
    results = []
    tokens = 0
    annToken=0
    fractalMatching = 0
    allSame = 0
    fileKeys = files.keys()
    numberOfAnnots = len(fileKeys)
    itterlen = min([len(files[f]) for f in fileKeys])
    if(len(set([len(files[f]) for f in fileKeys]))>1 or numberOfAnnots<5):
        print("Fajlovi cija duzina se razlikuje", [(whoseFile[a], len(files[a])) for a in fileKeys])
    for i in range(itterlen):
        itterFiles = [files[key][i] for key in fileKeys]
        if(itterFiles[0] != '' and itterFiles[0][0].isdigit()):
            tokens+=1
        if(min([len(each.split('\t')[-1]) for each in itterFiles])<1):
        # if(len(file1[i].split('\t')[-1])<1 or len(file2[i].split('\t')[-1])<1):
            continue
        allOpts = [each.split('\t')[-1] for each in itterFiles]
        diffs = set(allOpts)
        if(len(diffs)>1):
            maxAgreement = max(allOpts.count(dif) for dif in list(diffs))
            fractalMatching+=(numberOfAnnots-maxAgreement+1)/numberOfAnnots
            annToken += 1
        else:
            if (itterFiles[0] != '' and itterFiles[0].split('\t')[-1][-1] != 'O'):
                annToken += 1
                allSame += 1
                fractalMatching+=1
        # if(file1[i].split('\t')[-1][-1] != file2[i].split('\t')[-1][-1] or (file1[i].split('\t')[-1][-1]!='O' and (file1[i].split('\t')[-1][-5:]!= file2[i].split('\t')[-1][-5:])) ):
        #     # if(len(file1[i].split('\t')[-1])< and len(file1[i].split('\t')[-1])>1)
        #     print(file1[i].split('\t')[-1][-1] , file2[i].split('\t')[-1][-1])
        #     results.append("Razlika u fajlu url= "+filename+" na liniji: "+str(linesStartAt+i)+" (linije u pitanju: \""+file1[i]+"\" i \""+file2[i]+"\")")

    return (tokens, annToken,fractalMatching, allSame)

filesToCompare = dict()
whoseFile = dict()
for filename in glob.glob(os.path.join(path, '*.txt')):
    print(filename)
    with open(os.path.join(os.getcwd(), filename), 'r',encoding="utf8") as f: # open in readonly mode
        author = f.readline().replace(' ','').replace('\n','').split('=')[1]
        print(author)
        line = f.readline().replace(' ','').replace('\n','')
        while(line[0]=='#'):
            print(line.split('=')[0])
            if(line.split('=')[0]=='#anotator'):
                annotator = line.split('=')[1]
                print("annotator je ",annotator)
            elif(line.split('=')[0]=='#url'):
                filekey = line.split('=')[1]
                print("url je ",filekey)
            line = f.readline().replace(' ','').replace('\n','')
        if(filekey not in filesToCompare.keys()):
            filesToCompare[filekey]=dict()
        if (filekey not in whoseFile.keys()):
            whoseFile[filekey] = dict()
        whoseFile[filekey][annotator]=filename
        restOfLines=[]
        while(line):
            print(line)
            restOfLines.append(line.replace('\n',''))
            line = f.readline().replace(' ','')
        filesToCompare[filekey][annotator]=restOfLines
print(filesToCompare)
print(list(itertools.combinations(filesToCompare[list(filesToCompare.keys())[0]].keys(), 2)))
allMissmatches = dict()
anotatorStats = []
for each in (list(itertools.combinations(filesToCompare[list(filesToCompare.keys())[0]].keys(), 2))):
    missmatches=[]
    allTokens = 0
    allAnnTokens = 0
    for every in filesToCompare.keys():
        if(each[0] not in filesToCompare[every].keys() or each[1] not in filesToCompare[every].keys()):
            continue
        tokens, annTokens, misses =compareTwo(every ,filesToCompare[every][each[0]],filesToCompare[every][each[1]])
        missmatches+=["Tekstovi koji se posmatraju su:" +whoseFile[every][each[0]] +"  i "+whoseFile[every][each[1]] ]+misses
        allTokens+=tokens
        allAnnTokens+=annTokens
    allMissmatches[each]=(allTokens,missmatches)
    numberOfMistakes=len(missmatches)
    allAnnTokens+=numberOfMistakes
    anotatorStats.append(f"Statistika za anotatore {each[0]} i {each[1]} \n\tUkupan broj tokena: {allTokens} \n\tUkupan broj anotiranih tokena: {allAnnTokens} \n\tUkupan broj razlika: {numberOfMistakes} \n\tProcenat slicnosti anotiranih tokena: {((allAnnTokens-numberOfMistakes)/allAnnTokens*100)} \n\tProcenat slicnosti svih tokena: {((allTokens-numberOfMistakes)/allTokens*100)}\n")
    with open("razlike_" + each[0]+"_i_"+each[1]+".txt",'w', encoding='utf-8') as file:
        file.write(f"Ukupan broj tokena: {allTokens} \nUkupan broj anotiranih tokena: {allAnnTokens} \nUkupan broj razlika: {numberOfMistakes} \nProcenat slicnosti anotiranih tokena: {((allAnnTokens-numberOfMistakes)/allAnnTokens*100)} \nProcenat slicnosti svih tokena: {((allTokens-numberOfMistakes)/allTokens*100)} \nRazlike:\n")
        for missmatch in missmatches:
            file.write(missmatch+'\n')

allSame=0
fractal=0
allTokens = 0
allAnnTokens = 0
for every in filesToCompare.keys():
    # if(each[0] not in filesToCompare[every].keys() or each[1] not in filesToCompare[every].keys()):
    #     continue
    tokens, annTokens, fract , allS =compareAll(every ,filesToCompare[every], whoseFile[every])
    allTokens+=tokens
    allAnnTokens+=annTokens
    allSame+=allS
    fractal+=fract
print(allTokens)
print(allAnnTokens)
print(allSame)
print(fractal)
print(allSame/allAnnTokens*100)
print(fractal/allAnnTokens*100)
print((allSame+allTokens-allAnnTokens)/allTokens*100)
print((fractal+allTokens-allAnnTokens)/allTokens*100)
# allAnnTokens+=numberOfMistakes
with open("stepeniSaglasnosti.txt",'w', encoding='utf-8') as file:
    file.write(f"Ukupan broj tokena: {allTokens} \nUkupan broj anotiranih tokena: {allAnnTokens} \nProcenat slicnosti anotiranih tokena (svaki anotirani token ima vrednost izmedju 0 i 1 u zavisnosti od toga koliko anotatora se slaze): {(fractal/allAnnTokens*100)} \nProcenat slicnosti svih tokena (svaki anotirani token ima vrednost izmedju 0 i 1 u zavisnosti od toga koliko anotatora se slaze): {((fractal+allTokens-allAnnTokens)/allTokens*100)} \nProcenat slicnosti anotiranih tokena (anotirani tokeni se uzimaju kao dobro anotirani samo ako se svi anotatori slazu): {(allSame/allAnnTokens*100)} \nProcenat slicnosti svih tokena (anotirani tokeni se uzimaju kao dobro anotirani samo ako se svi anotatori slazu): {((allSame+allTokens-allAnnTokens)/allTokens*100)}\n")
    for every in anotatorStats:
        file.write(every)
#     for missmatch in missmatches:
#         file.write(missmatch+'\n')

# print(allMissmatches)
# print(len(allMissmatches[('ognjen', 'teodora')][1]))
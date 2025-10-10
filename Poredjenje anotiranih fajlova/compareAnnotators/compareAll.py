import os, glob
import itertools
path = 'toCompare'

linesStartAt=7

def compareTwo(filename, file1, file2):
    results = []
    tokens = 0
    annToken=0
    for i in range(len(file1)):
        if(file1[i] == '' or file1[i][0].isdigit()):
            tokens+=1
        if(file1[i]!=file2[i]):
            results.append("Razlika u fajlu url= "+filename+" na liniji: "+str(linesStartAt+i)+" (linije u pitanju: \""+file1[i]+"\" i \""+file2[i]+"\")")
        elif(file1[i] != '' and file1[i].split('\t')[-1]!='O'):
            annToken+=1
    return (tokens, annToken,results)

filesToCompare = dict()
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
        restOfLines=[]
        while(line):
            print(line)
            restOfLines.append(line.replace('\n',''))
            line = f.readline().replace(' ','')
        filesToCompare[filekey][annotator]=restOfLines
print(filesToCompare)
print(list(itertools.combinations(filesToCompare[list(filesToCompare.keys())[0]].keys(), 2)))
allMissmatches = dict()
for each in (list(itertools.combinations(filesToCompare[list(filesToCompare.keys())[0]].keys(), 2))):
    missmatches=[]
    allTokens = 0
    allAnnTokens = 0
    for every in filesToCompare.keys():
        if(each[0] not in filesToCompare[every].keys() or each[1] not in filesToCompare[every].keys()):
            continue
        tokens, annTokens, misses =compareTwo(every ,filesToCompare[every][each[0]],filesToCompare[every][each[1]])
        missmatches+=misses
        allTokens+=tokens
        allAnnTokens+=annTokens
    allMissmatches[each]=(allTokens,missmatches)
    numberOfMistakes=len(missmatches)
    allAnnTokens+=numberOfMistakes
    with open("razlike_" + each[0]+"_i_"+each[1]+".txt",'w', encoding='utf-8') as file:
        file.write(f"Ukupan broj tokena: {allTokens} \nUkupan broj anotiranih tokena: {allAnnTokens} \nUkupan broj razlika: {numberOfMistakes} \nRazlike:\n")
        for missmatch in missmatches:
            file.write(missmatch+'\n')

print(allMissmatches)
print(len(allMissmatches[('ognjen', 'teodora')][1]))
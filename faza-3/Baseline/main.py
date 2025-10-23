import glob
import os
from opcode import opname

from pandas import DataFrame
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_predict, KFold


def error(msg: str) -> None:
    print(f"\033[91m{msg}\033[0m")


def export(splited: list[str]) -> tuple[str, str]:
    try:
        return splited[1], splited[-1].strip()
    except IndexError:
        error(f"Line not in CoNLL format: {splited}")
        return "error", "O"


def remake(sentencte: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    tokens, labels = [], []
    for token, label in sentencte:
        tokens.append(token)
        labels.append(label)
    return tokens, labels


def load_conll_data(path) -> list[tuple[list[str], list[str]]]:
    sentences, sentence = [], []
    with open(path, encoding='utf-8') as file:
        for line in file:

            # ignore comments
            if line.startswith('#'):
                continue

            # check is this new line
            if line == '\n':
                if sentence:
                    sentences.append(remake(sentence))
                    sentence = []
                continue

            # process line
            splited = line.split('\t')
            sentence.append(export(splited))

    return sentences


def token_features(sentence, index):
    token = sentence[index]
    features = {
        'token': token.lower(),
        'is_capitalized': token[0].isupper(),
        'position': index,
    }
    # prethodna 2 tokena
    # todo: zasto samo 2 tokena?
    # todo: je l se gledaju naredni
    for i in range(1, 3):
        if index - i >= 0:
            prev = sentence[index - i]
            features['prev{i}_token'] = prev.lower()
            features['prev{i}_capitalized'] = prev[0].isupper()
        else:
            features['prev{i}_token'] = '<START>'
            features['prev{i}_capitalized'] = False
    return features


if __name__ == "__main__":
    # name = "test.txt"

    pathText = "..\\..\\faza-1\\Text fajlovi"
    pathAnnot = "..\\..\\faza-2\\anotirani_tekstovi"
    files = []
    for folder in glob.glob(os.path.join(pathAnnot, "*")):
        for filename in glob.glob(os.path.join(folder, '*.txt')):
            # print(filename)
            # anFile=pathAnnot+'\\'+ folder.split('\\')[-1]+'\\'+'annotated_'+filename.split('\\')[-1]
            # print(anFile)
            files.append(filename)
    #Izrada feature-a (osobina)
    data = []
    for file in files:
        data += load_conll_data(file)

    #Pretvaranje u DataFrame
    X, y = [], []

    for sentence, labels in data:
        for i in range(len(sentence)):
            X.append(token_features(sentence, i))
            y.append(labels[i])
            if labels[i] == 'ORG':
                print(sentence)

    df = DataFrame(X)
    df['label'] = y
    #print(df.head())

    #One-hot enkodiranje i priprema za model
    vec = DictVectorizer(sparse=True)
    X_vec = vec.fit_transform(df.drop(columns=['label']).to_dict(orient='records'))
    y_vec = df['label']

    #10-slojna unakrsna validacija
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    model = MultinomialNB()
    y_pred = cross_val_predict(model, X_vec, y_vec, cv=kf)
    print(classification_report(y_vec, y_pred, zero_division=0))

    #Evaluacija bez B-/I- prefiksa
    def strip_prefix(tag):
        return tag.split('-')[-1] if '-' in tag else tag

    y_true_stripped = [strip_prefix(t) for t in y_vec]
    y_pred_stripped = [strip_prefix(t) for t in y_pred]

    print("=== Evaluacija bez B-/I- prefiksa ===")
    print(classification_report(y_true_stripped, y_pred_stripped, zero_division=0))
    with open("results.txt",'w') as outFile:
        outFile.write('\nRezultati klasifikacionog izvestaja sa prefiksima \n')
        outFile.write(classification_report(y_vec, y_pred, zero_division=0))
        outFile.write('\nRezultati klasifikacionog izvestaja bez prefiksa \n')
        outFile.write(classification_report(y_true_stripped, y_pred_stripped, zero_division=0))
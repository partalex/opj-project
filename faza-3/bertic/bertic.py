import pandas as pd
from simpletransformers.ner import NERModel, NERArgs
import numpy as np

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
            token_info.append(word)
            token_info.append(label)

            result.append(token_info)
            token_info = []
            

    return result

if __name__ == "__main__":

    name = "test.txt"
    data = load_conll_data(name)
    print(data)

    model_data = pd.DataFrame(
        data, columns=["sentence_id", "words", "labels"]
    )
    print(model_data)

    
    model_args = NERArgs()
    model_args.labels_list = ['B-LOC','B-MISC','B-ORG','B-PER','I-LOC','I-MISC','I-ORG','I-PER','O']
    model = NERModel(
        "electra", "classla/bcms-bertic-ner", args=model_args, use_cuda=False
    )
    result, model_outputs, preds_list = model.eval_model(model_data)
    


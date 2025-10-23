import os, csv
from collections import defaultdict
from typing import Dict, List, Tuple
from sklearn.metrics import accuracy_score, classification_report
import classla
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report
import seaborn as sns

LANG = "sr"
MODEL_TYPE = "standard"
USE_GPU = True
RES_DIR =  os.path.normpath("../../faza-3/classla/classla_resources")
OUTPUT_DIR = r"../../faza-3/classla/out"
PATH_ANN = os.path.normpath("../../faza-2/anotirani_tekstovi")

os.makedirs(OUTPUT_DIR, exist_ok=True)

nlp = classla.Pipeline(
    LANG,
    type=MODEL_TYPE,
    processors="tokenize,ner",
    dir=RES_DIR,
    use_gpu=USE_GPU
)

def map_classla_type(t: str) -> str:
    """
    CLASSLA/BERTić: DERIV-PER -> PER, MISC -> O, ostalo ostaje.
    """
    if t == "DERIV-PER":
        return "PER"
    if t == "MISC":
        return "O"
    return t

def map_bio(tag: str) -> str:
    """
    Primeni mapiranje na BIO tag:
    - ako je O, ostaje O
    - ako je B-* ili I-*, mapiraj tip i vrati O ako mapiрање daje 'O'.
    """
    if tag == "O" or not tag:
        return "O"
    if "-" not in tag:
        # ako bi se desilo da tip dođe bez prefiksa, tretiraj kao entitet bez BIO
        typ_m = map_classla_type(tag)
        return "O" if typ_m == "O" else f"B-{typ_m}"
    pref, typ = tag.split("-", 1)
    typ_m = map_classla_type(typ)
    return "O" if typ_m == "O" else f"{pref}-{typ_m}"

def strip_bio(tag: str) -> str:
    return tag.split("-")[-1] if "-" in tag else tag

# =======================
# POMOĆNE FUNKCIJE: čitanje gold-a + rekonstrukcija teksta
# =======================
def load_gold_offsets_and_tags(file2: str) -> Tuple[Dict[int, List[str]], List[Tuple[str, bool]]]:
    """
    Učitava anotirani CoNLL i vraća:
      - annFiles: {start_offset: [token, GOLD_TAG, PRED_TAG]}
      - layout:   [(token, no_space_after: bool), ...] redom
    """
    annFiles: Dict[int, List[str]] = {}
    layout: List[Tuple[str, bool]] = []
    flen = 0
    with open(file2, 'r', encoding='utf-8') as f:
        for line in f:
            if len(line) > 2 and not line.startswith('#'):
                cols = line.rstrip('\n').split('\t')
                if cols[0].isnumeric():
                    tok = cols[1]
                    gold = cols[-1] if cols[-1] else 'O'
                    nosp = (len(cols) >= 10 and cols[-2] == "SpaceAfter=No")
                    annFiles[flen] = [tok, gold, 'O']
                    layout.append((tok, nosp))
                    flen += len(tok) if nosp else len(tok) + 1
    return annFiles, layout

def rebuild_text_from_gold_layout(layout: List[Tuple[str, bool]]) -> str:
    """Rekonstruiše tekst TAČNO kao u anotacijama (poštuje SpaceAfter=No)."""
    parts = []
    for tok, nosp in layout:
        parts.append(tok)
        if not nosp:
            parts.append(" ")
    return "".join(parts)

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

# =======================
# CLASSLA predikcija uz mapiranje DERIV-PER/MISC
# =======================
def run_classla_ner(text: str) -> Dict[str, List[Dict[str, int]]]:
    doc = nlp(text)
    buckets = defaultdict(list)
    for ent in doc.entities:
        et = map_classla_type(ent.type)  # ovde odmah mapiramo DERIV-PER->PER, MISC->O
        if et == "O":
            continue
        if et == "PER":
            key = "PERS"  # da bi se niže koristio postojeći tagMap
        elif et in ("LOC", "ORG"):
            key = et
        else:
            # sve ostalo nas ne zanima
            continue
        buckets[key].append({"start": ent.start_char, "end": ent.end_char})
    return dict(buckets)

# =======================
# Evaluacija jednog fajla (annotated_*.txt)
# =======================
def analize_file(file_gold: str):
    """
    Vraća:
      - liste: trueBIO_m, predBIO_m, trueCLS_m, predCLS_m (mapirane prema pravilima)
      - rows: za CSV (uključuje i mapirane kolone)
    """
    annFiles, layout = load_gold_offsets_and_tags(file_gold)
    text = rebuild_text_from_gold_layout(layout)

    # CLASSLA predikcije (već mapirano DERIV-PER/MISC)
    result = run_classla_ner(text)
    tagMap = {"PERS": ["B-PER", "I-PER"], "LOC": ["B-LOC", "I-LOC"], "ORG": ["B-ORG", "I-ORG"]}

    # popuni pred BIO po tokenima
    for k in set(["PERS", "LOC", "ORG"]).intersection(result.keys()):
        for ent in result[k]:
            if ent['start'] in annFiles:
                annFiles[ent['start']][2] = tagMap[k][0]  # B-*
                end = ent['end']
                # I-* za sve tokene unutar span-a
                for s in list(annFiles.keys()):
                    if s > ent['start'] and s < end:
                        annFiles[s][2] = tagMap[k][1]

    # napravi nizove i CSV redove (sa mapiranim kolonama)
    trueBIO_m, predBIO_m, trueCLS_m, predCLS_m = [], [], [], []
    rows = []
    for offset in sorted(annFiles.keys()):
        tok, gold, pred = annFiles[offset]
        gold_m = map_bio(gold)
        pred_m = map_bio(pred)
        trueBIO_m.append(gold_m)
        predBIO_m.append(pred_m)
        trueCLS_m.append(map_classla_type(strip_bio(gold)))
        predCLS_m.append(map_classla_type(strip_bio(pred)))
        rows.append({
            "file": os.path.basename(file_gold),
            "offset": offset,
            "token": tok,
            "gold": gold,
            "pred": pred,
            "gold_mapped": gold_m,
            "pred_mapped": pred_m,
            "match_mapped": int(gold_m == pred_m)
        })
    return trueBIO_m, predBIO_m, trueCLS_m, predCLS_m, rows

# =======================
# GLAVNI DEO
# =======================
if __name__ == "__main__":
    # 1) Skupi sve annotated_*.conllu osim EXCLUDE_DIR
    annotated_files: List[str] = []
    for entry in os.scandir(PATH_ANN):
        if not entry.is_dir():
            continue
        for root, _, files in os.walk(entry.path):
            for fn in files:
                if fn.lower().endswith(".conllu") and fn.startswith("annotated_"):
                    annotated_files.append(os.path.join(root, fn))
    annotated_files.sort()

    all_trueBIO_m, all_predBIO_m = [], []
    all_trueCLS_m, all_predCLS_m = [], []
    all_rows = []

    for fp in annotated_files:
        print("OBRAĐUJEM", fp)
        t_bio, p_bio, t_cls, p_cls, rows = analize_file(fp)
        all_trueBIO_m += t_bio
        all_predBIO_m += p_bio
        all_trueCLS_m += t_cls
        all_predCLS_m += p_cls
        all_rows += rows

    # 3) Metrike (mapirane)
    acc_bio = accuracy_score(all_trueBIO_m, all_predBIO_m) if all_trueBIO_m else 0.0
    acc_cls = accuracy_score(all_trueCLS_m, all_predCLS_m) if all_trueCLS_m else 0.0
    rep_bio = classification_report(all_trueBIO_m, all_predBIO_m, zero_division=0)
    rep_cls = classification_report(all_trueCLS_m, all_predCLS_m, zero_division=0)

    # 4) Upis fajlova
    csv_path = os.path.join(OUTPUT_DIR, f"classla_{MODEL_TYPE}_predictions_tokens_mapped.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["file","offset","token","gold","pred","gold_mapped","pred_mapped","match_mapped"]
        )
        writer.writeheader()
        writer.writerows(all_rows)

    report_path = os.path.join(OUTPUT_DIR, f"classla_{MODEL_TYPE}_report_mapped.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"CLASSLA NER evaluacija ({MODEL_TYPE}) — MAPIRANO (DERIV-PER→PER, MISC→O)\n")
        f.write(f"Ukupno tokena: {len(all_trueBIO_m)}\n")
        f.write(f"ACCURACY (BIO-level, mapped):   {acc_bio:.6f}\n")
        f.write(f"ACCURACY (entity-only, mapped): {acc_cls:.6f}\n\n")
        f.write("=== Token-level BIO (mapped) ===\n")
        f.write(rep_bio + "\n\n")
        f.write("=== Token-level entity-only (B/I ignorisan, mapped) ===\n")
        f.write(rep_cls + "\n")
    y_true_no_prefix = [label.split('-')[-1] if '-' in label else label for label in all_trueCLS_m]
    y_pred_no_prefix = [label.split('-')[-1] if '-' in label else label for label in all_predCLS_m]
    labels_list_no_prefix = ['LOC', 'ORG', 'PER', 'O']

    plot_confusion_matrix(y_pred_no_prefix, y_true_no_prefix, labels_list_no_prefix)
    print("ZAVRŠENO.")
    print("Sačuvano CSV:", csv_path)
    print("Sačuvano izveštaj:", report_path)

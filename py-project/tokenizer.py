import reldi_tokeniser

paragraph_list = []
with open("allText.txt", "r", encoding="utf-8") as f:
    content = f.read()
    temp_list = content.split("#")
    for el in temp_list:
        if el.startswith("text ="):
            value = el.split("=")[1].strip()
            output = reldi_tokeniser.run(value, 'sr', nonstandard=True, tag=True)
            paragraph_list.append(output + "\n")

with open("tokenizedSeperatly.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(paragraph_list))



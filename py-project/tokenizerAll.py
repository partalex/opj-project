import os
import shutil
import reldi_tokeniser

root_input_folder = "text_files"
root_output_folder = "tokenized_files"

for root, dirs, files in os.walk(root_input_folder):
    relative_path = os.path.relpath(root, root_input_folder)
    output_dir = os.path.join(root_output_folder, relative_path)
    os.makedirs(output_dir, exist_ok=True)

    for filename in files:
        if filename.endswith(".txt"):
            file_input_path = os.path.join(root, filename)
            file_output_path = os.path.join(output_dir, "tokenized_"+ filename)

            
            parts = []
            with open(file_input_path, "r", encoding = "utf-8") as f:
                text = f.read()
                parts = text.split("#")
                parts = [p.strip() for p in parts if p.strip()]

            with open(file_output_path, "a", encoding = "utf-8") as f:
                for p in parts:
                    if(p.startswith("text = ")):
                        value = p.split("=")[1].strip()
                        output = reldi_tokeniser.run(value, 'sr', nonstandard=True, tag=True)
                        lines = []

                        for line in output.split("\n"):
                            if line.strip() == "":  
                                lines.append("") 
                            elif line.strip()[0].isdigit():
                                lines.append(line + "\tO")
                            else:
                                lines.append(line)

                        conll_output = "\n".join(lines)
                        f.write(conll_output)
                    else:
                        f.write("#" + p + "\n")
            
            print(f"  ➝ Obradio fajl: {file_input_path} → {file_output_path}")

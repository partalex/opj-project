#!/bin/bash
# Rename all .txt files to .conllu recursively

find . -type f -name "*.txt" | while read -r file; do
    newname="${file%.txt}.conllu"
    mv -- "$file" "$newname"
    echo "Renamed: $file -> $newname"
done

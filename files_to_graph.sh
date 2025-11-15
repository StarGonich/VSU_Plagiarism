#!/bin/sh

export PATH="/home/alexey/bin/joern/joern-cli/bin:$PATH"

VENV_PYTHON="/home/alexey/VSU_Plagiarism/.venv/bin/python"

# Проверка аргумента
if [ -z "$1" ]; then
    echo "Usage: $(basename "$0") <path/to/directory>"
    exit 1
fi

# Обработка пути к директории
INPUT_DIR="$(realpath "$1" 2>/dev/null || echo "$1")"
if [ ! -d "$INPUT_DIR" ]; then
    echo "Directory \"$INPUT_DIR\" does not exist"
    exit 1
fi

# Цикл по всем файлам в директории
for INPUT_FILE in "$INPUT_DIR"/*; do
    # Пропускаем директории
    if [ ! -f "$INPUT_FILE" ]; then
        continue
    fi

    FILE_NAME=$(basename "$INPUT_FILE")
    BASE_NAME="${FILE_NAME%.*}"
    OUTPUT_DIR=$(dirname "$INPUT_FILE")

    echo "Processing $FILE_NAME..."

    # Команды Joern
    echo "Parsing $INPUT_FILE..."
    joern-parse "$INPUT_FILE" -o "cpg/${BASE_NAME}.bin"
    if [ $? -ne 0 ]; then
        echo "Failed to parse $INPUT_FILE"
        continue
    fi

    echo "Exporting representations..."
    mkdir -p "repr_all"
    joern-export "cpg/${BASE_NAME}.bin" --repr all --out "repr_all/${BASE_NAME}"
    mkdir -p "repr_pdg"
    joern-export "cpg/${BASE_NAME}.bin" --repr pdg --out "repr_pdg/${BASE_NAME}"

    # Объединение графов
    echo "Merging graphs..."
    mkdir -p "test_graphs"
    "$VENV_PYTHON" merge.py --pdg "repr_pdg/${BASE_NAME}/*-pdg.dot" --ref "repr_all/${BASE_NAME}/export.dot" -o "test_graphs/${BASE_NAME}.dot"

    echo "Successfully processed $FILE_NAME"
    echo "----------------------------------------"
done

echo "All files processed"

import os
import LogParser

# ИСПОЛЬЗОВАТЬ ТОЛЬКО 1 РАЗ, ибо в log файле нет привязок решений к файлам

folder_path = '602776_OK'
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

logparser = LogParser.LogParser('log.txt')
logparser.parse()

count = 0
print(f"Всего {len(files)}")
for i, file in enumerate(files):
    sub = logparser.submissions[i]
    filename, ext = os.path.splitext(file)
    print(ext)
    if sub.verdict != 'OK':
        count += 1
        print(f'Файл {folder_path}/{file} удалён')
        # os.remove(os.path.join(folder_path, file))
    elif ext in ('.pypy3-64', '.py3', '.pypy3'):
        newfilename = filename + '.py'
        os.rename(os.path.join(folder_path, file), os.path.join(folder_path, newfilename))

print(f"Удалено {count}")
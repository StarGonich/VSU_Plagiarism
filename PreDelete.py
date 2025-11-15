import os
import shutil

import LogParser

# ИСПОЛЬЗОВАТЬ ТОЛЬКО 1 РАЗ, ибо в log файле нет привязок решений к файлам

LOGPATH = 'log.txt'
ARCHIVEPATH = '602776'
ARCHIVEPATH_OK = ARCHIVEPATH + '_OK'

# Создаем папку для правильных решений
if not os.path.exists(ARCHIVEPATH_OK):
    os.makedirs(ARCHIVEPATH_OK)

logparser = LogParser.LogParser(LOGPATH, ARCHIVEPATH)
logparser.parse()

count = 0
print(f"Всего {len([sub for sub in logparser.submissions])}")
# Создать папку 602776_OK
for sub in logparser.submissions:
    filename, ext = os.path.splitext(sub.filename)
    # print(ext)
    if sub.verdict == 'OK':
        count += 1
        # Обрабатываем расширения файлов
        if ext in ('.pypy3-64', '.py3', '.pypy3'):
            fullfilename = filename + '.py'
            source_file = os.path.join(ARCHIVEPATH, sub.filename)
            target_file = os.path.join(ARCHIVEPATH_OK, fullfilename)

            # Переименовываем и копируем в новую папку
            if os.path.exists(source_file):
                os.rename(source_file, os.path.join(ARCHIVEPATH, fullfilename))
                shutil.copy2(os.path.join(ARCHIVEPATH, fullfilename), target_file)
        else:
            fullfilename = filename + ext
            source_file = os.path.join(ARCHIVEPATH, sub.filename)
            target_file = os.path.join(ARCHIVEPATH_OK, fullfilename)

            # Копируем файл в новую папку
            if os.path.exists(source_file):
                shutil.copy2(source_file, target_file)

print(f"Правильных {count}")
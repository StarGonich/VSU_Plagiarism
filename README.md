1) Установка Joern 4.0.xxx версии, и Python (у меня используется 3.13)
2) Запуск bat файла, где в качестве параметра используется директория с программами
```shell
.\files_to_graph.bat .\programs\
```
В итоге появится несколько папок, но нас в основном интересует graphs, где находятся PDG графы наших программ.

3) Запуск main.py, где берутся графы из директории graphs и сравниваются. По итогу создаётся `plagiarism_log.txt`, где хранится вывод
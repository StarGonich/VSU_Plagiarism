from LogParser import LogParser

LOGPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\log.txt"
ARCHIVEPATH = r"C:\Users\Alexey\Documents\VKR\VSU_Plagiarism\602776"

logparser = LogParser(LOGPATH, ARCHIVEPATH)
logparser.parse()

for p in logparser.problems:
    subs = [sub for sub in p.submissions if sub.verdict == 'OK']
    print(p.code, len(subs))
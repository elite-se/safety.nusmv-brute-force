import argparse
import datetime
import os
import shutil
import time
from subprocess import Popen
from util.smvFileParser import extractChecks


# https://stackoverflow.com/a/51212150/6319588
def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(string)


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def setupWorkDir(outPath: str):
    if outPath is 'None':
        shutil.rmtree('temp', ignore_errors=True)
        os.mkdir('temp')
        return 'temp'
    return outPath


parser = argparse.ArgumentParser()
parser.add_argument('--path', type=file_path, required=True, help='Path to the .smv file you want to check')
parser.add_argument('--nusmv', type=file_path, required=True, help='Path to Nusmv executable')
parser.add_argument('--outpath', type=dir_path, help='Optional output directory. If not set, using temp')

args = parser.parse_args()

workDirectory = setupWorkDir(args.outpath)

with open(args.path, 'r') as smvFile:
    smvFileContent = smvFile.read()

smvWithoutChecks, smvChecks = extractChecks(smvFileContent)

with open(os.path.join(workDirectory, smvWithoutChecks.smv), 'w') as smvWithoutChecksFile:
    smvWithoutChecksFile.writelines(smvWithoutChecks)

for index, check in enumerate(smvChecks):
    print("Id %i: %s" % (index, check))

selectedChecksString = input('Select checks to run, e.g.: (1,3,7) or leave empty to run all: ').strip()

if selectedChecksString is not "":
    selectedChecksList = list(map(lambda check: int(check.strip()), selectedChecksString.split(",")))
    assert len(selectedChecksList) > 0
    smvChecks = [smvChecks[i] for i in selectedChecksList]

fileNames = []
for index, check in enumerate(smvChecks):
    print("Id %i: %s" % (index, check))
    fileName = os.path.join(workDirectory, ("smvWithCheck%i.smv" % index))
    fileNames.append(os.path.abspath(fileName))
    with open(fileName, 'w') as svmCheckFile:
        svmCheckFile.writelines(smvWithoutChecks)
        svmCheckFile.write(check)

pipes = []
processes = []
openFiles = []

startTime = time.time_ns()
print("Starting processes at " + datetime.datetime.now().strftime("%H:%M:%S"))
for index, path in enumerate(fileNames):
    fileName = os.path.join(workDirectory, ('out%i.txt' % index))
    outFile = open(fileName, 'w')
    openFiles.append(outFile)
    process = Popen([args.nusmv, path], stdout=outFile, stderr=outFile)
    processes.append(process)

try:
    while True:
        totalProcesses = len(processes)
        finishedProcesses = []
        ongoingProcesses = []
        for index, process in enumerate(processes):
            if process.poll() is None:
                ongoingProcesses.append(index)
            else:
                finishedProcesses.append(index)
        if len(ongoingProcesses) is 0:
            print()
            break
        print("Active processes: %s, finished: %s" % (''.join(str(proc) + ',' for proc in ongoingProcesses), ''.join(str(proc) + ',' for proc in finishedProcesses)), end='\r')
        time.sleep(5)
except KeyboardInterrupt:
    for index, process in enumerate(processes):
        try:
            process.terminate()
        except OSError:
            pass
        process.wait()
        openFiles[index].close()

for openFile in openFiles:
    openFile.close()

afterTime = time.time_ns()
print("Finished after %f ms" % ((afterTime - startTime) / 1000000))

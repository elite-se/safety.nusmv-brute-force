import argparse, os
import shutil
from subprocess import Popen, PIPE
import time, datetime

# https://stackoverflow.com/a/51212150/6319588
def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=file_path, required=True, help='Path to the .smv file you want to check')
parser.add_argument('--nusmv', type=file_path, required=True, help='Path to Nusmv executable')

args = parser.parse_args()

shutil.rmtree('temp',ignore_errors=True)
os.mkdir('temp')

with open(args.path, 'r') as smvFile:
    smvFileContent = smvFile.read()

smvFileLines = smvFileContent.splitlines()

smvWithoutChecks = []
smvChecks = []
checkConcluded = True

for line in smvFileLines:
    if line.startswith('CTLSPEC') or line.startswith('LTLSPEC'):
        checkConcluded = True
        smvChecks.append(line)
        if ";" not in line:
            checkConcluded = False
    elif checkConcluded or line.startswith('DEFINE') or line.startswith('--') or line.isspace():
        # this line does not belong to a check anymore
        smvWithoutChecks.append(line + '\n')
        checkConcluded = True
    else:
        # this is a multiline LTL/CTL Spec
        smvChecks[-1] += ' ' + line.replace('\t', ' ').replace('  ', ' ')
        

with open('temp/smvWithoutChecks.smv', 'w') as smvWithoutChecksFile:
    smvWithoutChecksFile.writelines(smvWithoutChecks)

fileNames = []
for index, check in enumerate(smvChecks):
    print("Id %i: %s" % (index, check))
    fileName = "temp/smvWithCheck%i.smv" % index
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
    fileName = 'temp/out%i.txt' % index
    outFile = open(fileName, 'w')
    openFiles.append(outFile)
    process = Popen([args.nusmv, path], stdout=outFile, stderr=outFile)
    processes.append(process)

try:
    while True:
        time.sleep(5)
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

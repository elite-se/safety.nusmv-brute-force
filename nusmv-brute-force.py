import datetime
import os
import shutil
import time
from subprocess import Popen
from util.smvFileParser import extractChecks
from util.argumentParser import parseArguments
from util.configFileParser import parseConfig
import re


def setupWorkDir(outPath: str):
    if outPath is None:
        shutil.rmtree('temp', ignore_errors=True)
        os.mkdir('temp')
        return 'temp'
    return outPath


def checkForFailedChecks(subDir: str = 'temp/'):
    outFileRegex = re.compile('out[0-9]+\\.txt')
    allOutputFiles = [f for f in os.listdir(subDir) if outFileRegex.match(f)]

    failedChecks = []
    passedChecks = []

    for outputFile in allOutputFiles:
        with open(subDir + outputFile, 'r') as openOutputFile:
            fileContent = openOutputFile.read()

            if 'as demonstrated by the following execution sequence' in fileContent:
                failedChecks.append(outputFile)
            else:
                passedChecks.append(outputFile)

    passedChecksNumbers = []

    for passedCheck in passedChecks:
        checkNumber = re.search('out([0-9]+).txt', passedCheck)
        passedChecksNumbers.append(checkNumber.group(1))

    print('The following checks passed: ' + ','.join(passedChecksNumbers))

    failedChecksNumbers = []

    for failedCheck in failedChecks:
        checkNumber = re.search('out([0-9]+).txt', failedCheck)
        failedChecksNumbers.append(checkNumber.group(1))

        os.rename(subDir + failedCheck, subDir + failedCheck + '.failed')

    print('The following checks failed: ' + ','.join(failedChecksNumbers))


smvPath, nusmvPath, outPath, configFile = parseArguments()

if smvPath is None or nusmvPath is None:
    # require config
    configSmvPath: str
    configNusmvPath: str
    if configFile is not None:
        configSmvPath, configNusmvPath = parseConfig(configFile)
    else:
        configSmvPath, configNusmvPath = parseConfig()
    if smvPath is None:
        smvPath = configSmvPath
    if nusmvPath is None:
        nusmvPath = configNusmvPath

workDirectory = setupWorkDir(outPath)

with open(smvPath, 'r') as smvFile:
    smvFileContent = smvFile.read()

smvWithoutChecks, smvChecks = extractChecks(smvFileContent)

with open(os.path.join(workDirectory, 'smvWithoutChecks.smv'), 'w') as smvWithoutChecksFile:
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
    process = Popen([nusmvPath, path], stdout=outFile, stderr=outFile)
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
        print("Active processes: %s; finished: %s" % (
            ','.join(str(proc) for proc in ongoingProcesses), ','.join(str(proc) for proc in finishedProcesses)),
              end='\r')
        time.sleep(1)
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

checkForFailedChecks()

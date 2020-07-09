def extractChecks(smvFileContent: str):
    smvFileLines = smvFileContent.splitlines()
    checkConcluded = True
    smvWithoutChecks = []
    smvChecks = []
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

    return smvWithoutChecks, smvChecks
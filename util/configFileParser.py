import configparser


def parseConfig(configFile: str = 'config.ini'):
    configParser = configparser.ConfigParser()
    configParser.read(configFile)

    smvFile = configParser['main']['SmvFile']
    nusmvPath = configParser['main']['NusmvPath']
    return smvFile, nusmvPath

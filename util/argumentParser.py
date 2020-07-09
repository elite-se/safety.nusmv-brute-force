import argparse
import os

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


def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=file_path, help='Path to the .smv file you want to check')
    parser.add_argument('--nusmv', type=file_path, help='Path to Nusmv executable')
    parser.add_argument('--outpath', type=dir_path, help='Optional output directory. If not set, using temp')
    parser.add_argument('--config', type=file_path, help='Optional config file location')

    args = parser.parse_args()

    smvPath: str = args.path
    nusmvPath: str = args.nusmv
    outPath: str = args.outpath
    configFile: str = args.config
    return smvPath, nusmvPath, outPath, configFile

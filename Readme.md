# Brute forcing nuSMV

### How it works

Splits all LTLs and CTLs at the end of the .smv file and starts a nusmv instance for every formula.
The output is saved in the temp folder. The temp folder gets deleted when starting the process!

Multi line LTLs and CTLs should work

### Run

`python .\nusmv-wrapper.py --path="" --nusmv=""`

Where path is the .smv file and nusmv the nusmv executable file

Tested with Python 3.7.7 64-bit on Windows 10.

**Caution: Starting the program with complex setups might need more than 10GB of RAM. It might even freeze your PC if you're unlucky.**

### Benchmark

- Normal execution: 18 min 30 seconds
- Brute-force execution: 7 min

### Limitations

- The outputs aren't processed, only stored into files. It would be nice to display which checks failed
- A keyboard interrupt on Console should kill all nusmv processes. This does not work if the process is started with an IDE like VsCode.
- No batch mode with an upper limit is possible yet. Your PC might get fried
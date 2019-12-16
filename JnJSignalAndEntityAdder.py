import sys
import os
import csv
import re

def usage():
    print("Usage: python JnNSignalAndEntityAdder.py [-h] -i inputDir [-o outDir] -s sizeMB")
    print("where:")
    print("\t-h - OPTIONAL displays these instructions.")
    print("\tinputDir - Path to input directory containing files")
    print("\tsizeMB - The maximum size of the resulting files")
    print("\toutputDir - OPTIONAL - Path to output directory where to place created files.")
    print("\t\tDefault=Output (subdirectory added to input directory")
    print("Program creates 'Narrow' format files to be imported into Falkonry not to exceed sepecified size in MB.")
    print("File are created from csv files with tag values where tag names are assumed to be 020_Entity_Signal.")
    print("Example:")
    print("\t020_Autoclave6_Active_SubPhase_Number where Entity='Autoclave6' and Signal=SubPhase_Number.")
    print("The timestamp of the signal value is the preceding column.")
    print("The timestamp format is assumed to be supported by Falkonry (e.g. m/d/yyyy h:m, etc.).")
    print("Empty Signal values are not added to output files.")
    print("The output files will be named same as input files with a subindex '*_n'.")
    print("Example:")
    print("\t2016_1_0.csv where '_0' is a sequential number for each file created in order to meet the maximum size.")
    sys.exit(1)

def processargs():
    indir = None
    outdir = None
    filesize = None
    # Arg processing
    if((len(sys.argv)>1 and "-h" in map(lambda a:a.lower(),sys.argv)) or len(sys.argv)<5 ):
        usage()
    for i in range(1, len(sys.argv), 2):
        arg = sys.argv[i].lower()
        val = sys.argv[i + 1]
        if arg == "-i":
            indir = val
        elif arg == "-o":
            outdir = val
        elif arg == "-s":
            try:
                filesize=int(val)
                if(filesize<=0):
                    print("filesize must be a positive integer")
                    sys.exit(1)
            except ValueError:
                print("%s is not a valid integer value for filesize" % val)
                sys.exit(1)
        else:
            print("Unknown argument %s" % arg)
    if(not indir):
        print("Input directory not specified")
        usage()
    elif(not os.path.isdir(indir)):
        print("Input directory %s is not valid" % indir)
        sys.exit(1)
    return indir,outdir,filesize

def handleoutputdir(outdir,indir):
    if(not outdir):
        outdir=os.path.join(indir,"Output")
    if(not os.path.exists(outdir)):
        os.mkdir(outdir)
    # Empty sub directory
    for f in os.listdir(outdir):
        if(f.lower().endswith(".csv")):
            os.remove("%s%s%s" % (outdir,os.sep,f))
    return outdir

def getEntityAndSignal(col):
    entity=col[col.index('_',0)+1:col.index('_',4)]
    signal=col[col.index('_',4)+1:]
    return (entity,signal)

def getColumnMappings(header):
    mappings={}  # odd column number -> entity -> signal
    cols=header.split(',')
    for i,col in enumerate(cols):
        if ((i+1)%2==0):
            mappings[i-1]=getEntityAndSignal(col)
    return mappings



def main():
    # process args
    indir,outdir,filesize=processargs()

    # Handle output directory
    outdir=handleoutputdir(outdir,indir)

    # process files in indir
    mappings={}
    for f in os.listdir(indir):
        if(f.lower().endswith(".csv") and not(f.lower().startswith("alarm"))): # skip alarm headers file just in case
            # initialize file indexing
            firstLine = True
            fn = 0
            fout = None
            sizeBytes = 0
            fpathout = None
            fpathin = "%s%s%s" % (indir,os.sep,f)
            fileprefix=f[0:f.index('.csv')]
            lnum=1
            with open(fpathin) as fin:
                try:
                    # read line
                    line=fin.readline()
                    while(line):
                        # if first line store mappings to values
                        if(firstLine):
                            print("Reading from file %s" % fpathin)
                            mappings=getColumnMappings(line)
                            firstLine=False
                        else:
                            # split line at command
                            parts=line.split(',')
                            lines=[] # lines to write to output
                            # combine into several lines with entity and signal
                            for i,part in enumerate(parts):
                                if((i+1)%2==0):
                                    entity,signal=mappings[i-1]
                                    # if no timestamp or value skip
                                    ts=parts[i-1].strip()
                                    val=parts[i].strip()
                                    if(not(val) or not(ts) or val=="Bad"):
#                                        print("Skipping %s + %s in line %s of file %s, due to missing value or timestamp" % (entity,signal,lnum,f))
                                        continue
                                    l=",".join([ts,val,entity,signal])+os.linesep
                                    lines.append(l)
                            # if no file open, do it and add header
                            if (not fout or fout.closed):
                                # open file
                                fpathout= "%s%s%s_%s.csv" % (outdir, os.sep, fileprefix, fn)
                                print("Writing to file %s" % fpathout)
                                fout = open(fpathout, 'wb')
                                # write header
                                strout = "timestamp,value,entity,signal%s" % os.linesep
                                btout = strout.encode('UTF-8')
                                fout.write(btout)
                                sizeBytes=len(btout)
                            # write lines
                            for lineout in lines:
                                btout= lineout.encode('UTF-8')
                                fout.write(btout)
                                sizeBytes += len(btout)
                            # check size and close file if needed
                            if(sizeBytes>=filesize*1024*1024):
                                fn+=1
                                fout.close()
                        line = fin.readline()
                        lnum+=1
                except IOError:
                    print("IO Error when writing to file %s" % fpathout)
                finally:
                    # close last file for that tag
                    if(fout and not fout.closed):
                        fout.close()
if __name__ == "__main__":
    main()



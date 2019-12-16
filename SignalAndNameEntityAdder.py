import sys
import os
import csv
import re

def usage():
    print("Usage: python SignalAndEntityAdder.py [-h] -i inputDir [-o outDir] -m mapFile -s sizeMB")
    print("where:")
    print("\t-h - OPTIONAL displays these instructions.")
    print("\tinputDir - Path to input directory containing files")
    print("\tmapFile - Path to mapping file. File contains a header and rows with:")
    print("\t\t signal,entity,tag values that allow creating proper signal files")
    print("\tsizeMB - The maximum size of the resulting files")
    print("\toutputDir - OPTIONAL - Path to output directory where to place created files.")
    print("\t\tDefault=Output (subdirectory added to input directory")
    print("Program creates files to be imported into Falkonry not to exceed sepecified size in MB from")
    print("csv files generated from PI in the format timestamp,value (no header).")
    print("The file name is assumed to be the name of the PI point/tag (e.g. 20272PI.PV.csv for tag 20272PI.PV.")
    print("The timestamp format is assumed to be supported by Falkonry (e.g. yyyy-MM-dd HH:mm:ss, etc.).")
    print("The output files will be by PI point/tag name with special characters replaced.")
    print("\tExample: 0272PI_PV_0.csv where '_0' is a sequential number for each file created in order to meet the maximum size.")
    sys.exit(1)

"""
mapfile format example - PLEASE CHECK WITH SME to complete this file. What I show here is only an example
    and may not even be correct for the files received so far.  This is just for illustration purposes.
    
entity,signal,tag
Compressor1,InletTemp,10272TI.PV
Compressor2,InletTemp,10272PI.PV
Compressor1,InletPress,20272TI.PV
Compressor2,InletPress,20272PI.PV
Compressor1,MotorSpeed,10272SI.PV
Compressor1,FilterDiffPress,90272PDI.PV
Compressor2,FilterDiffPress,90272PDI.PV
Compressor1,Flow,10272FI.PV
    
    ... some signals are common to both and hence they must be repeated, e.g. 90272PDI.PV
    ... you should have same signal names for each entity (tags may be different)
    ... if an entity has less signals than another, model can only be trained with common signal OR
    ... different models will be required for each entity
    
"""
def processargs():
    indir = None
    outdir = None
    filesize = None
    mapfile = None
    # Arg processing
    if((len(sys.argv)>1 and "-h" in map(lambda a:a.lower(),sys.argv)) or len(sys.argv)<7 ):
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
        elif arg == "-m":
            mapfile = val
        else:
            print("Unknown argument %s" % arg)
    if(not indir):
        print("Input directory not specified")
        usage()
    elif(not os.path.isdir(indir)):
        print("Input directory %s is not valid" % indir)
        sys.exit(1)
    if(not mapfile):
        print("Map file not not specified")
        usage()
    elif (not os.path.exists(mapfile)):
        print("Map file %s does not exist" % indir)
        sys.exit(1)
    return indir,outdir,mapfile,filesize

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

# tagname -> entity -> signal
def getmappings(mapfile):
    mappings={}
    with open(mapfile,'r') as f:
        r=csv.DictReader(f)
        for line in r:
            entity=line['entity']
            tag=line['tag']
            signal=line['signal']
            if(not tag in mappings):
                mappings[tag]={}
            if (not signal in mappings[tag]):
                mappings[tag][signal]= set() # set of entities
            if(entity in mappings[tag][signal]):
                raise ValueError("duplicate signal %s for entity % in file %s" % (signal, entity, mapfile))
            mappings[tag][signal].add(entity)
    return mappings

def main():
    # process args
    indir,outdir,mapfile,filesize=processargs()

    # Handle output directory
    outdir=handleoutputdir(outdir,indir)

    # get maps to signals and tags
    tags=getmappings(mapfile)

    # process files in indir
    for f in os.listdir(indir):
        if(f.lower().endswith(".csv")):
            start=f.rfind(os.sep)
            end=f.lower().index(".csv")
            # get tagname
            tagname=f[(start+1):end]
            fileprefix=re.sub('\W+','_',tagname)
            print("processing values for tag %s" % tagname)

            # get entities and signals to write out
            signals=tags[tagname]

            with open("%s%s%s" % (indir,os.sep,f)) as fin:
                reader=csv.reader(fin)
                # initialize file indexing
                fn = 0
                fout=None
                sizeBytes = 0
                fpath=None
                try:
                    for line in reader:
                        timestamp=line[0]
                        value=line[1]
                        # for each signal
                        for signal,entities in signals.items():
                            # if no file open, do it
                            if (not fout or fout.closed):
                                # open file
                                fpath="%s%s%s_%s.csv" % (outdir, os.sep, fileprefix, fn)
                                fout = open(fpath, 'wb')
                                # write header
                                strout = "timestamp,value,signal,entity%s" % os.linesep
#                                strout = "timestamp,value,señal,entity%s" % os.linesep
                                btout = strout.encode('UTF-8')
                                fout.write(btout)
                                sizeBytes=len(btout)
                            # write line for each entity
                            for entity in entities:
                                strout="%s,%s,%s,%s%s" % (timestamp,value,signal,entity,os.linesep)
                                btout= strout.encode('UTF-8')
                                fout.write(btout)
                                sizeBytes += len(btout)
                            if(sizeBytes>=filesize*1024*1024):
                                fn+=1
                                fout.close()
                except IOError:
                    print("IO Error when writing to file %s" % fpath)
                finally:
                    # close last file for that tag
                    if(fout and not fout.closed):
                        fout.close()

if __name__ == "__main__":
    main()



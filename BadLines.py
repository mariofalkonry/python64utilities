import os


def handleoutputdir(indir,outdir=None):
    if(not outdir):
        outdir=os.path.join(indir,"Output")
    if(not os.path.exists(outdir)):
        os.mkdir(outdir)
    # Empty sub directory
    for f in os.listdir(outdir):
        if(f.lower().endswith("cleaned.csv")):
            os.remove("%s%s%s" % (outdir,os.sep,f))
    return outdir

def main():
    headerlength=0
    indir="C:\\Users\\m2bre\\Documents\\Projects\\Aptar\\Data\\Electrical_Data"
    filefilter=lambda f:f.endswith("Signals.csv") and not(f.endswith("cleaned.csv"))
    isgoodline=lambda l:len(l.split(","))>=headerlength

    # Walk directory writing lines to output minus empty lines
    outdir = handleoutputdir(indir)
    firstfile=True
    for dirname, subdirlist, filelist in os.walk(indir):
        for fname in filelist:
            if filefilter(fname):
                with open(os.path.join(dirname,fname),"r") as fin:
                    outfile=os.path.join(outdir,fname.replace(".csv","cleaned.csv"))
                    with open(outfile,"w+") as fout:
                        line=fin.readline()
                        if(firstfile):
                            headerlength=len(line.split(","))
                            firstfile=False
                        while(line):
                            if(isgoodline(line)):
                                fout.write(line)
                            else:
                                print("Found bad line: %s" % line)
                            line=fin.readline()
if __name__ == "__main__":
    main()
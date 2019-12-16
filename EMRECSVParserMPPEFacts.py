import pandas as pd
import os
import re
import traceback

def readEntities(entitiesFile):
    df=pd.read_csv(entitiesFile,header=None,columns=["entity"])
    return df["entity"].toList()

def processFacts(entities,factsFile):
    for entry in os.scandir(fileDirectory):
        # Only daily files at this time
        if (entry.path):
            try:
                facts = getPandasFrame(entry.path)
                csvpath = entry.path.replace('.hdf5', '.csv')
                df.to_csv(csvpath, index=False)
                print("Saving File: %s" % csvpath)
            except Exception:
                print("Error processing file: %s" % entry.path)
                traceback.print_exc()

    df=pd.read_excel()
df=pd.read_csv(file,nrows=rowswithName-1)
# build column names for signals
colnames=[]
for col in df.columns:
    colname = (col if col != "Unnamed" else "timestamp")
    rows=df[col].to_list()
    for row in rows:
        strRow=str(row)
        if(strRow!="NaN"):
            colname=colname+" "+strRow
    colnames.append(colname)
colnames[0]="timestamp"
# now read the values
df=pd.read_csv(file,header=None,skiprows=rowswithName,names=colnames,low_memory=False)
df["timestamp"]=df["timestamp"].str.replace("-06:00","").str.replace("-05:00","")
df["entity"]=[entity]*df.shape[0]
df.to_csv(file.replace(".csv","_falkonry.csv"),index=False)


if __name__ == "__main__":
    # TODO: Arg processing
    fileDirectory = "C:\\Users\\m2bre\\Documents\\Projects\\XOM R&E\\HPPE Share"
    entitiesFile = "Data\\MPPEEntities.txt"
    filePattern = r'Facts.xslx'

    # Load entities
    entities=readEntities(entitiesFile)


    # Load vessels reference
    with open(vesselsFile) as f:
        reader=csv.reader(f,)
        for row in reader:
            key = row[0]
            if key in vessels:
                raise ValueError("entity: %s is defined more than once" % key)
            vessels[key] = row[1]

    processFiles(rootDir)

    # TODO: Load Via Web API to save time
import pandas as pd
import  BatchGenerators.BatchGenerator as bgen
boolAddBatch=True
rowWithTagName=2
headerRows=3
entity=""
file="C:\\Users\\m2bre\\Documents\\Code\\python\\Falkonry64\\Coker+Refoam+Batch\\Coker+Refoam+Batch.csv"
df=pd.read_csv(file, header=None, nrows=rowWithTagName)
# build column names for signals
colnames=[]
for col in df.columns:
    colname=df[col][0]
    if(not(colname)):
        colname="time"
    colnames.append(colname)
# now read the values
df=pd.read_csv(file,header=None,skiprows=headerRows,names=colnames,low_memory=False)
df["timestamp"]=df["timestamp"].str.replace("-06:00","").str.replace("-05:00","")
df["entity"]=[entity]*df.shape[0]
df.to_csv(file.replace(".csv","_falkonry.csv"),index=False)
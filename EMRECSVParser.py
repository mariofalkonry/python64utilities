import pandas as pd
rowswithName=1
entity="BTRF MEK Unit"
file="C:\\Users\\m2bre\\Documents\\Projects\\XOM R&E\\BTRF MEK FILTERS\\LUMDCPSDATA2015.csv"
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
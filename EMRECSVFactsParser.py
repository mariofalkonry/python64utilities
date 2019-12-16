import pandas as pd
import copy
rowswithName=1
entity="BTRF MEK Unit"
file="C:\\Users\\m2bre\\Documents\\Projects\\XOM R&E\\BTRF MEK FILTERS\\LUMDCPSDATA2016_falkonry.csv"
valveTags=['LUMDR0701','LUMDR0801','LUMDR0901','LUMDR1001','LUMDR1101','LUMDR1201']
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
df=pd.read_csv(file,header=None,skiprows=rowswithName,names=colnames,index_col="timestamp",low_memory=False)
# create series of filter
prevStates=dict.fromkeys(valveTags,"")
currentFact=dict.fromkeys(valveTags)
facts=[]
for ts in df.index.values:
    valveState=df.loc[ts,valveTags]
    if(valveState.empty):
        print(f"No valve tags found for ts: {ts}")
        continue
    for valve in valveTags:
        state=None
        if(valveState[valve] is pd.Series):
            print(f"More than one value found for valve tag {valve} for ts: {ts}")
            state=valveState[valve][0]
        else:
            state=valveState[valve]
        if(state==u"CLOSED"):
            if(prevStates[valve]!=u"CLOSED"):
                prevStates[valve]=u"CLOSED"
                currentFact[valve]={'starTime':ts,'endtime':None,'entity':entity,'value':'Filter Cleaning','keyword':valve}
        else:
            # capture fact if coming from closed (end of wash cycle)
            if(prevStates[valve]==u"CLOSED"):
                # set endtime of not a bad pv
                if(state!=u"BADPV"):
                    currentFact[valve]['endtime']=ts
                # store in facts dictionary
                facts.append(copy.deepcopy(currentFact[valve]))
            prevStates[valve]=valveState[valve]
dfacts=pd.DataFrame(facts)
dfacts.to_csv(file.replace(".csv","_facts_falkonry.csv"),index=False)
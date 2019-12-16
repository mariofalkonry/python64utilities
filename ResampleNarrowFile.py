import pandas as pd
file="C:\\Users\\m2bre\\Documents\\Falkonry\\Demos\\XHQ\\SignalDataForFalkonryDemo.csv"
tscolumn="ts"
valcolumn="value"
signalcolumn="signal"
# load to df
df=pd.read_csv(file,usecols=[tscolumn,valcolumn,signalcolumn])
df[tscolumn]=pd.to_datetime(df[tscolumn])
df[valcolumn]=pd.to_numeric(df[valcolumn])
#df.set_index(tscolumn)
# pivot
df=df.pivot(index=tscolumn,columns=signalcolumn,values=valcolumn)
# interpolate columns not in index at 15 minutes interval
for col in df.columns:
    # interpolate series
    series=df[col]
    print(series)
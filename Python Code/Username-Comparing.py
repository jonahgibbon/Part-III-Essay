import pandas as pd
from jaro import jaro_winkler_metric as jw_metric
from timeit import default_timer as timer
from Levenshtein import distance



forums=['Stormfront','Incelsis','Incelsnet','Lookism','RooshV','Pickartist','Mgtow','Gyow','Kiwifarms']
directory='/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/Data/'
time='20180101'
masterData=[]
for m in forums:
    df = pd.read_csv(directory+time+'/'+m+time+'.csv')
    masterData.append(list(set(df['creator'].tolist())))

a=3  
print(len(masterData[a]))
new=list(set([str(x).lower() for x in masterData[a]]))
print(len(new))

start=timer()
print(jw_metric('Margerine','Marge'))
end=timer()
print(end-start)


start=timer()
print(distance('Margerine','Marge'))
end=timer()
print(end-start)

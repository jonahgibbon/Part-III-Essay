import pandas as pd
import numpy as np
import math
from timeit import default_timer as timer
from itertools import combinations
from datetime import datetime as dt
from copy import deepcopy
from Levenshtein import distance
from jaro import jaro_winkler_metric as jw_metric


start=timer()

def find_indices(given_list,item):
    indices=[]
    for i in enumerate(given_list):
        if i[1]==item:
            indices.append(i[0])
    return(indices)

    return H
def remove_pairs(forum,name,masterPairs):
    for s in range(forum):
        deletes=[]
        for item in masterPairs[s][forum]:
            if item[1]==name:
                deletes.append(item)
        for item in deletes:
            masterPairs[s][forum].remove(item)
    for s in range(forum,len(masterPairs)):
        deletes=[]
        for item in masterPairs[forum][s]:
            if item[0]==name:
                deletes.append(item)
        for item in deletes:
            masterPairs[forum][s].remove(item)
    return masterPairs;


forums=['Stormfront','Incelsis','Incelsnet','Lookism','RooshV','Pickartist','Mgtow','Gyow','Kiwifarms']
n=len(forums)
time='20180101'
directory='/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/Data/'


threshold=1
fuzz=1

masterData=[]
for m in forums:
    df = pd.read_csv(directory+time+'/'+m+time+'.csv')
    masterData.append(df['creator'].tolist())
    masterData.append(df['created_on'].tolist())
pairs=list(combinations(list(range(n)),2))
masterPairs=[[[]for i in range(n)] for j in range(n)]
masterPairs_numeric=np.zeros((n,n),dtype=np.int16)


##Partition usernames by size
masterNames=[]
for i in range(n):
    names=list(set(masterData[2*i]))
    lengths = [len(str(name)) for name in names]
    longest_string=len(names[lengths.index(max(lengths))])
    masterNames.append([[] for num in range(longest_string+1)])
    for name in names:
        masterNames[i][len(str(name))].append(str(name))

##Iterate through pairs to find similar names
for pcnt in range(int(n*(n-1)/2)):
    a=str(round(100*pcnt/len(pairs),2))+'% done'
    print(a,end="\r")
    
    if len(masterNames[pairs[pcnt][0]])<=len(masterNames[pairs[pcnt][1]]):
        mem_sml=deepcopy(masterNames[pairs[pcnt][0]])
        mem_big=deepcopy(masterNames[pairs[pcnt][1]])
        flip=0
    else:
        mem_sml=deepcopy(masterNames[pairs[pcnt][1]])
        mem_big=deepcopy(masterNames[pairs[pcnt][0]])
        flip=1

##  FIND EXACT MATCHES 
    candidates=[]
    for sml_cnt in range(0,len(mem_sml)):
        for sml_name in mem_sml[sml_cnt]:
            if sml_name in mem_big[sml_cnt]:
##                CHECK DISTRIBUTION
                candidates.append([sml_name,sml_name])
    for item in candidates:
        masterPairs[pairs[pcnt][0]][pairs[pcnt][1]].append(item)
        masterPairs_numeric[pairs[pcnt][0]][pairs[pcnt][1]]+=1
        mem_sml[len(item[0])].remove(item[0])
        mem_big[len(item[0])].remove(item[0])

##  FIND FUZZY MATCHES
    for sml_cnt in range(0,len(mem_sml)):
        if len(mem_sml)==len(mem_big):
            mem_range=range(max([0,sml_cnt-fuzz]),min([len(mem_sml),sml_cnt+fuzz]))
        else:
            mem_range=range(max([0,sml_cnt-fuzz]),min([len(mem_sml)+1,sml_cnt+fuzz+1])) 
        for sml_name in mem_sml[sml_cnt]:
            break_flag=0
            for big_cnt in mem_range:
                for big_name in mem_big[big_cnt]:
                    if jw_metric(sml_name,big_name)>=0.9:
##                        CHECK DISTRIBUTION HERE
                        if flip==0:
                            masterPairs[pairs[pcnt][0]][pairs[pcnt][1]].append([sml_name,big_name])
                        else:
                            masterPairs[pairs[pcnt][0]][pairs[pcnt][1]].append([big_name,sml_name])
                        masterPairs_numeric[pairs[pcnt][0]][pairs[pcnt][1]]+=1
                        mem_big[big_cnt].remove(big_name)
                        break_flag=1
                        break
                if break_flag==1:
                    break
                
mid=timer()
print(masterPairs_numeric)


##Build data table
cnt=0
table=np.zeros((2**n-1,n+1),dtype=np.int16)
for m in range(1,n+1):
    comb=list(combinations(list(range(len(forums))),m))
    for i in range(len(comb)):
        for j in range(len(comb[i])):
            table[cnt][comb[i][j]]=1
        cnt=cnt+1

##Enter in combinations of usernames greater than 3
cnt=n
data_cnt=2**n-2
while cnt>=3:
    comb=list(combinations(list(range(n)),cnt))
    for i in range(len(comb)):
        i=len(comb)-1-i
        current_comb=comb[i]
        candidates=[]
        for name in masterPairs[current_comb[0]][current_comb[1]]:
            candidates.append([name])
        for j in range(cnt-2):
            test_names=masterPairs[current_comb[j+1]][current_comb[j+2]]
            for can in candidates:
                flag=0
                if [] not in can:
                    for l in range(len(test_names)):
                        if can[j][1]==test_names[l][0]:
                            can.append([test_names[l][0],test_names[l][1]])
                            flag=1
                            break
                    if flag==0:
                        can.append([])
                else:
                    can.append([])
        for item in candidates:
            if [] not in item:
                if cnt>=4:
                    print(item)
                table[data_cnt][len(forums)]+=1
                masterPairs=remove_pairs(current_comb[0],item[0][0],masterPairs)
                for subItem in range(cnt-1):
                    masterPairs=remove_pairs(current_comb[subItem+1],item[subItem][1],masterPairs)                 
        data_cnt-=1
    cnt-=1

##Enter in pairs of usernames
for i in range(len(pairs)):
    pair=pairs[int(len(forums)*(len(forums)-1)/2-1-i)]
    for j in masterPairs[pair[0]][pair[1]]:
        table[data_cnt][len(forums)]+=1
    data_cnt-=1

##Complete the table
for i in range(n):
    i=n-1-i
    cnt=0
    for j in table:
        if j[i]==1:
            cnt=cnt+j[n]
    table[data_cnt][n]=len(set(masterData[2*i]))-cnt
    data_cnt-=1

##Shorten the table for output
short_table=np.zeros((1,n+1)).astype(int)
for row in table:
    if row[n]!=0:
        short_table=np.vstack([short_table,row])
short_table=np.delete(short_table,0,axis=0)
print(short_table)

end=timer()
print("Elapsed Time: "+str(round(end-start,2)))

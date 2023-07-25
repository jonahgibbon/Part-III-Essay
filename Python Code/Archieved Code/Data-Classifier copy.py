import pandas as pd
import numpy as np
import math
from timeit import default_timer as timer
from itertools import combinations
from datetime import datetime as dt
from copy import deepcopy

start=timer()

def fuzzy(a,b):
    if abs(len(a)-len(b))==1:
        if len(a)<len(b):
            small=a
            big=b
        else:
            small=b
            big=a
        n=0
        while n<=len(big)-1:
            check=list(big)
            del check[n]
            check=''.join(check)
            if check==small:
                return 1;
            else:
                n=n+1
        return 0;
    else:
        n=0
        while n<=len(a)-1:
            check1=list(a)
            del check1[n]
            check1=''.join(check1)
            check2=list(b)
            del check2[n]
            check2=''.join(check2)
            if check1==check2:
                return 1;
            else:
                n=n+1
        return 0;

def find_indices(given_list,item):
    indices=[]
    for i in enumerate(given_list):
        if i[1]==item:
            indices.append(i[0])
    return(indices)

def entropy(dist):
    H=0
    for i in range(len(dist)):
        if dist[i]!=0:
            H=H-dist[i]*math.log(dist[i],2)
    return H


forums=['Stormfront','Incelsis','Incelsnet','Lookism','RooshV','Pickartist','Mgtow','Gyow','Kiwifarms']
n=len(forums)
time='20180101'
directory='/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/Data/'
threshold=1

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
    print(str(round(100*pcnt/len(pairs),2))+'% done')
    candidates=[]
    if len(masterNames[pairs[pcnt][0]])<=len(masterNames[pairs[pcnt][1]]):
        mem_sml=deepcopy(masterNames[pairs[pcnt][0]])
        mem_big=deepcopy(masterNames[pairs[pcnt][1]])
    else:
        mem_sml=masterNames[pairs[pcnt][1]].copy()
        mem_big=masterNames[pairs[pcnt][0]].copy()
    for sml_cnt in range(0,len(mem_sml)):

        if len(mem_sml)==len(mem_big):
            mem_range=range(max([0,sml_cnt-1]),min([len(mem_sml),sml_cnt+1]))
        else:
            mem_range=range(max([0,sml_cnt-1]),min([len(mem_sml)+1,sml_cnt+2]))

        for sml_name in mem_sml[sml_cnt]:
            break_flag=0
            for big_cnt in mem_range:
                for big_name in mem_big[big_cnt]:
                    if fuzzy(sml_name,big_name)==1:
##                        CHECK DISTRIBUTION HERE
                        masterPairs[pairs[pcnt][0]][pairs[pcnt][1]].append([sml_name,big_name])
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
                table[data_cnt][len(forums)]+=1
                for subItem in range(cnt-1):
                    masterPairs[current_comb[subItem]][current_comb[subItem+1]].remove(item[subItem])
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

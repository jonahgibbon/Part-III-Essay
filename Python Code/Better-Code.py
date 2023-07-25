import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from itertools import combinations
from jaro import jaro_metric


def score(compare):
    compare['time_score']=(compare['kappa_x']*compare['R_x']+compare['kappa_y']*compare['R_y']-(compare['kappa_x']*\
                            compare['R_y']+compare['kappa_y']*compare['R_x'])*(compare['mu1_x']*compare['mu1_y']+\
                            compare['mu2_x']*compare['mu2_y']))/2
##  BUILD POST CONTENT COMPARISION *** UNDER CONSTRUCTION
    compare['content_score']=0
    compare['score']=compare['time_score']+compare['content_score']
    compare['removed']=0
    compare=compare.sort_values(by=['score']).reset_index(drop=True)
    return compare;

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
    
start=timer()
forums=['Stormfront','Incelsis','Incelsnet','Lookism','RooshV','Pickartist','Mgtow','Gyow','Kiwifarms']


n=len(forums)
time='20180101'

mast_df=pd.DataFrame({'creator':pd.Series(dtype='string'),
                      'forum':pd.Series(dtype='int8'),
                      'mu1':pd.Series(dtype='float64'),
                      'mu2':pd.Series(dtype='float64'),
                      'R':pd.Series(dtype='float64'),
                      'kappa':pd.Series(dtype='float64'),
                      'tot_posts':pd.Series(dtype='int64'),
                      'null_posts':pd.Series(dtype='int64'),
                      'link_posts':pd.Series(dtype='int64'),
                      'len_posts_av':pd.Series(dtype='object')})
directory='/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/New_Data/'

for forum_index in range(len(forums)):
    read_df=pd.read_csv(directory+time+'/'+forums[forum_index]+time+'.csv')
    read_df['not_a_reply']=read_df['not_a_reply'].astype('category')
    read_df['created_on']=pd.to_datetime(read_df['created_on'],format='%Y-%m-%d %H:%M:%S')
    read_df['created_on']=math.pi*(3600*read_df['created_on'].dt.hour+60*read_df['created_on'].dt.minute\
                                   +read_df['created_on'].dt.second)/43200
    read_df['created_on']=pd.to_numeric(read_df['created_on'])
    read_df[['comp1','comp2']]=np.zeros((len(read_df),2))
    read_df['comp1']=read_df['created_on'].apply(np.cos)
    read_df['comp2']=read_df['created_on'].apply(np.sin)
    
##  This calculates the von Mises parameters
    sml_df=read_df[['creator','comp1','comp2']].groupby(['creator']).sum()
    sml_df[['comp1','comp2']]=sml_df[['comp1','comp2']].div(read_df.groupby('creator').size(),axis=0)
    sml_df[['comp3','comp4']]=np.zeros((len(sml_df),2))
    sml_df['comp4']=read_df.groupby('creator').size()
    sml_df['comp3']=np.sqrt(sml_df['comp1']**2+sml_df['comp2']**2)
    sml_df[['comp1','comp2']]=sml_df[['comp1','comp2']].div(sml_df['comp3'],axis=0)
    sml_df['comp3']=sml_df['comp3']*sml_df['comp4'].div(sml_df['comp4']+0.25)
    sml_df['comp4']=sml_df['comp3']*(2-sml_df['comp3']).div(1-sml_df['comp3']**2,axis=0)
    sml_df.rename(columns={'comp1':'mu1','comp2':'mu2','comp3':'R','comp4':'kappa'},inplace=True)
    
##  This counts null posts, total posts and posts with links in. It also removes empty posts for further anlaysis.
    sml_df[['tot_posts','null_posts','link_posts']]=np.zeros((len(sml_df),3)).astype(int)
    creator_list=read_df.loc[(read_df['content'].isnull()==1)&(read_df['creator'].isnull()==0),'creator']
    sml_df.loc[creator_list,'null_posts']=creator_list.groupby(creator_list).size()
    read_df=read_df.drop(read_df[read_df['content'].isnull()==1].index)
    sml_df.loc[read_df['creator'],'tot_posts']=read_df[['creator','content']].groupby('creator').size()
    sml_df['tot_posts']=sml_df['tot_posts'].astype('int64')
    creator_list=read_df['creator'].loc[read_df['content'].str.contains("https://","www.")==1]
    sml_df.loc[creator_list,'link_posts']=creator_list.groupby(creator_list).size()

    
##  This is the start of the pre-processing content analysis *** UNDER CONSTRUCTION
    sml_df['len_posts_av']=np.zeros(len(sml_df))
    read_df['comp1']=read_df['content'].str.len()
    sml_df.loc[read_df['creator'],'len_posts_av']=read_df[['creator','comp1']].groupby('creator').sum()['comp1']
    sml_df['len_posts_av']=sml_df['len_posts_av'].div(read_df.groupby('creator').size()).astype('float32')
##  This is the end of the pre-processing content analysis

    
##  This appends the data to the master frame
    sml_df=sml_df.reset_index()
    sml_df['creator']=sml_df['creator'].astype('string')
    sml_df['forum']=forum_index
    mast_df=pd.concat([mast_df,sml_df],ignore_index=True,sort=False)
    
mast_df=mast_df.reset_index(drop=True)
end=timer()
print('Data pre-processed in '+str(round(end-start,2))+' seconds')

plt.hist(list(mast_df['len_posts_av']),bins=5000)
plt.xlim(0,2500)
plt.show()



masterPairs=[[[]for i in range(n)] for j in range(n)]
pair_combs=list(combinations(range(n),2))
for pair_cnt in range(int(n*(n-1)/2)):
    progress= str(round(pair_cnt*200/(n*(n-1)),2))+' percent complete'
    print(progress,end='\r')
##  This finds exact matches and scores them
    forum1=int(pair_combs[pair_cnt][0])
    df_1=mast_df.loc[mast_df['forum']==forum1]
    forum2=int(pair_combs[pair_cnt][1])
    df_2=mast_df.loc[mast_df['forum']==forum2]
    compare=df_1.merge(df_2,how='inner',on='creator')
    compare=score(compare)
    for entry in range(len(compare)):
        if compare.loc[entry,'removed']==0 and compare.loc[entry,'time_score']<1:
            masterPairs[forum1][forum2].append((compare.loc[entry,'creator'],compare.loc[entry,'creator']))
            df_1=df_1.drop(df_1.index[df_1['creator']==compare.loc[entry,'creator']])
            df_2=df_2.drop(df_2.index[df_2['creator']==compare.loc[entry,'creator']])

##  This finds exact matches after capitalization, and chooses the best match
    mod_df_1=df_1.reset_index()
    mod_df_2=df_2.reset_index()
    mod_df_1['creator']=mod_df_1['creator'].str.upper()
    mod_df_2['creator']=mod_df_2['creator'].str.upper()
    compare=mod_df_1.merge(mod_df_2,how='inner',on='creator')
    compare=score(compare)
    compare=compare.drop(compare.index[compare['time_score']>=1])
    compare=compare.sort_values(by=['time_score']).reset_index(drop=True)
    for entry in range(len(compare)):
        if compare.loc[entry,'removed']==0 and compare.loc[entry,'time_score']<1:
            masterPairs[forum1][forum2].append((df_1['creator'].loc[compare.loc[entry,'index_x']],\
                                                df_2['creator'].loc[compare.loc[entry,'index_y']]))
            df_1=df_1.drop(compare.loc[entry,'index_x'])
            df_2=df_2.drop(compare.loc[entry,'index_y'])
            compare.loc[compare.index[compare['index_x']==compare.loc[entry,'index_x']],'removed']=1
            compare.loc[compare.index[compare['index_y']==compare.loc[entry,'index_y']],'removed']=1
            
##  This finds exact matches after spaces and underscores are removed and chooses the best match
    mod_df_1=df_1.reset_index()
    mod_df_2=df_2.reset_index()
    mod_df_1['creator']=mod_df_1['creator'].str.replace(' ','').str.upper()
    mod_df_1['creator']=mod_df_1['creator'].str.replace('_','').str.upper()
    mod_df_2['creator']=mod_df_2['creator'].str.replace(' ','').str.upper()
    mod_df_2['creator']=mod_df_2['creator'].str.replace('_','').str.upper()
    compare=mod_df_1.merge(mod_df_2,how='inner',on='creator')
    compare=score(compare)
    compare=compare.drop(compare.index[compare['time_score']>=1])
    compare=compare.sort_values(by=['time_score']).reset_index(drop=True)
    for entry in range(len(compare)):
        if compare.loc[entry,'removed']==0 and compare.loc[entry,'time_score']<1:
            masterPairs[forum1][forum2].append((df_1['creator'].loc[compare.loc[entry,'index_x']],\
                                                df_2['creator'].loc[compare.loc[entry,'index_y']]))
            df_1=df_1.drop(compare.loc[entry,'index_x'])
            df_2=df_2.drop(compare.loc[entry,'index_y'])
            compare.loc[compare.index[compare['index_x']==compare.loc[entry,'index_x']],'removed']=1
            compare.loc[compare.index[compare['index_y']==compare.loc[entry,'index_y']],'removed']=1

##  This finds fuzzy matches after capitalization, and chooses the best one
    mod_df_1=df_1.reset_index()
    mod_df_2=df_2.reset_index()
    mod_df_1['creator']=mod_df_1['creator'].str.replace(' ','').str.upper()
    mod_df_1['creator']=mod_df_1['creator'].str.replace('_','').str.upper()
    mod_df_2['creator']=mod_df_2['creator'].str.replace(' ','').str.upper()
    mod_df_2['creator']=mod_df_2['creator'].str.replace('_','').str.upper()
    compare=pd.merge(mod_df_1,mod_df_2,how='cross')
    compare=score(compare)
    compare=compare.drop(compare.index[compare['time_score']>=1])
    compare['name_score']=compare.apply(lambda x:jaro_metric(x['creator_x'],x['creator_y']),axis=1)
    compare=compare.drop(compare.index[compare['name_score']<0.85])
    compare=compare.sort_values(by=['name_score','time_score'],ascending=[False,True]).reset_index(drop=True)
    for entry in range(len(compare)):
        if compare.loc[entry,'removed']==0:
            masterPairs[forum1][forum2].append((df_1['creator'].loc[compare.loc[entry,'index_x']],\
                                                df_2['creator'].loc[compare.loc[entry,'index_y']]))
            df_1=df_1.drop(compare.loc[entry,'index_x'])
            df_2=df_2.drop(compare.loc[entry,'index_y'])
            compare.loc[compare.index[compare['index_x']==compare.loc[entry,'index_x']],'removed']=1
            compare.loc[compare.index[compare['index_y']==compare.loc[entry,'index_y']],'removed']=1

another_end=timer()
print('Data fuzzy matched in '+str(round(another_end-end,2))+' seconds')

##This enters combinations into the table
table=np.zeros((2**n-1,n+1),dtype=np.int16)  
combination_size_cnt=n
table_row_cnt=2**n-2
while combination_size_cnt>=3:
    combs=list(combinations(list(range(n)),combination_size_cnt))
    for combs_cnt in range(len(combs)):
        combs_cnt=len(combs)-1-combs_cnt
        current_comb=combs[combs_cnt]
        for entry in current_comb:
            table[table_row_cnt,entry]=1
        candidates=[]
        for first_name in masterPairs[current_comb[0]][current_comb[1]]:
            candidates.append([first_name])
        for comb_entry_cnt in range(combination_size_cnt-2):
            test_names=masterPairs[current_comb[comb_entry_cnt+1]][current_comb[comb_entry_cnt+2]]
            for can in candidates:
                flag=0
                if [] not in can:
                    for test_name_cnt in range(len(test_names)):
                        if can[comb_entry_cnt][1]==test_names[test_name_cnt][0]:
                            can.append((test_names[test_name_cnt][0],test_names[test_name_cnt][1]))
                            flag=1
                            break
                    if flag==0:
                        can.append([])
        for can in candidates:
            if [] not in can:
                table[table_row_cnt,n]+=1
                masterPairs=remove_pairs(current_comb[0],can[0][0],masterPairs)
                for subItem in range(combination_size_cnt-1):
                    masterPairs=remove_pairs(current_comb[subItem+1],can[subItem][1],masterPairs)                 
        table_row_cnt-=1
    combination_size_cnt-=1
    
pairs=list(combinations(range(n),2))
for pair_cnt in range(int(n*(n-1)/2)):
    pair_cnt=int(n*(n-1)/2)-1-pair_cnt
    pair=pairs[pair_cnt]
    table[table_row_cnt,pair[0]]=1
    table[table_row_cnt,pair[1]]=1
    table[table_row_cnt,n]=len(masterPairs[pair[0]][pair[1]])
    table_row_cnt-=1

for i in range(n):
    i=n-1-i
    cnt=0
    for j in table:
        if j[i]==1:
            cnt=cnt+j[n]
    table[table_row_cnt,n]=len(mast_df.loc[mast_df['forum']==i])-cnt
    table[table_row_cnt,i]=1
    table_row_cnt-=1

##Shorten the table for output and exports the complete table
short_table=np.zeros((1,n+1)).astype(int)
for row in table:
    if row[n]!=0:
        short_table=np.vstack([short_table,row])
short_table=np.delete(short_table,0,axis=0)
print(short_table)
export_df=pd.DataFrame(table)
export_df.to_csv('/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/New_Data/20180101/Table_20180101.csv')

final=timer()
print('Programme completed in '+str(round(final-start,2))+' seconds')



##THINGS TO WORK ON
##Read NLP paper and cybercrime paper, making notes
##Apply for Machine Learning job
##Talk to Nick's cantab people
##Effectivly compare content being posted, giving a score to what's posted

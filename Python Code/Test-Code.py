import pandas as pd
from itertools import combinations, product


df_1=pd.DataFrame(data={'creator': ['Jonah_Gibbon', 'Jonah','Thomas','Monk','Mink'],
                        'created_on': ['2018-07-03 23:07:58','2018-07-03 21:07:58','2018-07-03 22:07:58',\
                                       '2018-07-03 21:07:58','2018-07-03 21:07:58'],
                        'content':['Hello there',"I'm also here","Here's a link https://jonahgibbontheboss","Pig","Nope"],
                        'not_a_reply':['t','t','t','f','f']})
df_2=pd.DataFrame(data={'creator': ['Thomas', 'jOnah giBBoN','jonah','Groner'],
                        'created_on': ['2018-07-03 23:07:58','2018-07-03 00:12:58','2018-07-03 18:07:58',\
                                       '2018-07-03 00:08:58'],
                        'content':['Hello there',"I'm also here","Here's a link https://jonahgibbontheboss","Dog"],
                        'not_a_reply':['t','t','t','t']})
df_1.to_csv('/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/New_Data/20180101/df_120180101.csv')
df_2.to_csv('/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/New_Data/20180101/df_220180101.csv')

print(df_1)
print(df_2)
x=list(combinations(range(4),4))
print(x)
print(x[0])
print(x[0][0])

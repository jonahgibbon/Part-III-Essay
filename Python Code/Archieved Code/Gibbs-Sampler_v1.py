import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import math
from timeit import default_timer as timer
from iteround import saferound

def find_overlap(num,data):
    s=0
    cnt=-1
    while s<num:
        s=s+data[cnt,len(data[0])-1]
        cnt=cnt+1
    return cnt;
def find_indices(data):
    indices=[]
    for i in range(len(data)):
        if data[i,len(data[0])-1]!=0:
            indices.append(i)
    return indices;

def gibbs(iterates,M,A,time):
    MainStart=timer()
    directory='/Users/jonahgibbon/Documents/Measuring-the-Unmeasurable/Data/ExtremeBB/'
    data=np.array(pd.read_csv(directory+time+'.csv',header=None))
    data_indices=find_indices(data)
    a_1=A[0]
    a_2=A[1]
    K=len(data[0])-1
    n=data.sum(axis=0)[K]

    ##CREATE TABLES AND LOAD START STATES
    alpha_tb=np.zeros(iterates)
    pi_tb=np.zeros((iterates,M))
    z_tb=np.zeros((iterates,n)).astype(int)
    theta_tb=np.zeros((iterates,K,M))
    n_tb=np.zeros(iterates).astype(int)
    omega_tb=np.zeros((iterates,M)).astype(int)
    alpha_tb[0]=A[0]*A[1]
    pi_tb[0,0]=1/(1+alpha_tb[0])
    for i in range(1,len(pi_tb[0])-1):
        pi_tb[0,i]=pi_tb[0,0]*((1-pi_tb[0,0])**i)
    pi_tb[0,len(pi_tb[0])-1]=(1-pi_tb[0,0])**(M-1)
    z_tb[0]=np.random.choice(range(M),n,p=pi_tb[0])
    for i in range(K):
        for j in range(M):
            theta_tb[0,i,j]=1/2
    n_tb[0]=2*n
    omega_tb[0]=saferound((n_tb[0]-n)*pi_tb[0],places=0)

    ##ITERATE THROUGH ALGORITHM
    for cnt in range(1,iterates):
        if (10*cnt)%iterates==0:
            end=timer()
            print(str(round(100*cnt/iterates,0))+' percent done in '+str(round(end-MainStart,1))+' seconds')
    ##    SAMPLE FROM Z
        datacnt=0
        n_k=np.zeros(M)
        n_jk=np.zeros((K,M))
        for i in data_indices:
            x=data[i,0:K:1]
            pos_indices=np.where(x==1)[0]
            neg_indices=np.where(x==0)[0]
            prob=np.ones(M)
            for k in range(M):
                for j in pos_indices:
                    prob[k]=prob[k]*theta_tb[cnt-1,j,k]
                for j in neg_indices:
                    prob[k]=prob[k]*(1-theta_tb[cnt-1,j,k])
                prob[k]=prob[k]*pi_tb[cnt-1,k]
            prob=prob/sum(prob)
            z_tb[cnt,datacnt:datacnt+data[i,K]:1]=np.random.choice(range(M),data[i,K],p=prob)
            for k in list(set(z_tb[cnt,datacnt:datacnt+data[i,K]:1])):
                a=np.count_nonzero(z_tb[cnt,datacnt:datacnt+data[i,K]:1]==k)
                n_k[k]=n_k[k]+a
                for j in pos_indices:
                    n_jk[j,k]=n_jk[j,k]+a
            datacnt=datacnt+data[i,K]
    ##    SAMPLE FROM THETA
        for i in range(K):
            for j in range(M):
                theta_tb[cnt,i,j]=np.random.beta(n_jk[i,j]+1,n_k[j]-n_jk[i,j]+omega_tb[cnt-1,j]+1)
                
    ##    SAMPLE FROM PI
        c_k=n_k+omega_tb[cnt-1]
        carry=np.zeros(M)
        for i in range(M):
            carry[i]=np.random.beta(1+c_k[i],alpha_tb[cnt-1]+sum(c_k[i+1:M:1]))
        carry[M-1]=1
        pi_tb[cnt]=np.ones(M)
        for i in range(M-1):
            pi_tb[cnt,i]=pi_tb[cnt,i]*carry[i]
            pi_tb[cnt,i+1:M:1]=pi_tb[cnt,i+1:M:1]*(1-carry[i])

    ##    SAMPLE FROM ALPHA
        alpha_tb[cnt]=np.random.gamma(A[0]-1+M,A[1]-math.log(pi_tb[cnt,M-1]))

    ##    SAMPLE FROM N
        carry=np.ones(M)
        for i in range(M):
            for j in range(K):
                carry[i]=carry[i]*(1-theta_tb[cnt,j,i])
            carry[i]=carry[i]*pi_tb[cnt,i]
        n_tb[cnt]=np.random.negative_binomial(n,1-sum(carry))+n

    ##    SAMPLE FROM OMEGA
        omega_tb[cnt]=np.random.multinomial(n_tb[cnt]-n,carry/sum(carry))
    MainEnd=timer()
    print('Completed in '+str(round(MainEnd-MainStart,2))+' seconds')
    return(n_tb,n);

def expectation(n_tb,pdf):
    minimum=(min(n_tb)+max(n_tb))/2-4.5*(max(n_tb)-min(n_tb))
    maximum=(min(n_tb)+max(n_tb))/2+4.5*(max(n_tb)-min(n_tb))
    x=np.linspace(minimum,maximum,num=5000,endpoint=True)
    pdf_vals=pdf.evaluate(x)
    s=0
    for i in range(len(x)):
        s=s+x[i]*pdf_vals[i]
    return s*(maximum-minimum)/4999

def plot_pdf(n_tb,pdf):
    minimum=(min(n_tb)+max(n_tb))/2-0.6*(max(n_tb)-min(n_tb))
    maximum=(min(n_tb)+max(n_tb))/2+0.6*(max(n_tb)-min(n_tb))
    x=np.linspace(minimum,maximum,num=5000,endpoint=True)
    pdf_vals=pdf.evaluate(x)
    plt.plot(x,pdf_vals,'k-')
    plt.xlabel('x')
    plt.ylabel('P(N=x)')
    

time=['20180101','20180401','20180701','20181001']
iterates=10000
M=100
A=[1,1/2]
spill=1000

for t in time:
    n_tb,n=gibbs(iterates,M,A,t)
    n_tb=n_tb[round(iterates/2):iterates:1]
    pdf=sp.stats.gaussian_kde(n_tb)
    exp=round(expectation(n_tb,pdf))
    print('Expectation: '+str(exp))
##    plot_pdf(n_tb,pdf)







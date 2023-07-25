K=9;
Iterates=1;
N=1000;
probs=zeros(2^K,Iterates);
Data=zeros(2^K,Iterates);

cnt=1;
while cnt<=Iterates
    a=10;
    b=5;
    Index=1;
    cnt1=0;
    while cnt1<=K
        S=nchoosek(K,cnt1);
        probs(Index:Index+S-1,cnt)=gamrnd(a,b,S,1);
        cnt1=cnt1+1;
        a=a/2;
        Index=Index+S;
    end
    probs(:,cnt)=probs(:,cnt)/sum(probs(:,cnt));
    Data(:,cnt)=mnrnd(N,probs(:,cnt));
    cnt=cnt+1;
end
Data=Data(2:end,:);
writematrix(Data,"TestData.csv")
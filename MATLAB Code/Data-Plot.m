Smth=1;
XTime=[
    datetime("2018-01-01")
    datetime("2018-04-01")
    datetime("2018-07-01")
    datetime("2018-10-01")
    datetime("2019-01-01")
    datetime("2019-04-01")
    datetime("2019-07-01")
    datetime("2019-10-01")    
    datetime("2020-01-01")
    datetime("2020-04-01")
    datetime("2020-07-01")
    datetime("2020-10-01")
    datetime("2021-01-01")
    ];
MidXTime=NaT(12,1);
cnt=1;
while cnt<=size(XTime,1)-1
    d=days(XTime(cnt+1)-XTime(cnt));
    MidXTime(cnt)=XTime(cnt)+d/2;
    cnt=cnt+1;
end
    
Data=[
    22115 24034.1 25657.9 27456.5 30500 25675.4 1069.5 12425 
    16488 16975.4 17802.0 18765.5 19828 17831.9 543.5 11927
    18342 19172.4 20305.5 21398.4 22527 20290.8 681.6 13174 
    23377 25212.7 26898.0 28848.7 30399 26925.1 1107.0 13293
    29119 31154.4 33559.3 35885.0 37638 33508.1 1437.8 14888
    34939 37016.7 40109.7 43562.4 46749 40126.9 1977.9 14691
    22043 23100.7 24628.7 26493.4 28454 24680.6 1035.8 14651
    25741 27213.0 28889.2 31842.1 33786 29127.1 1401.5 12973
    27301 29265.9 31083.7 33603.4 36659 31186.7 1353.8 14724
    38275 39957.5 42924.0 45853.6 49000 42935.0 1754.2 16916
    23461 24640.7 25843.4 27248.7 28908 25888.9 815.7 17054
    33545 35354.5 37506.0 40067.3 41653 37560.9 1412.5 16643
    ];

XNum=zeros(size(MidXTime,1),1);
cnt=1;
while cnt<=size(MidXTime,1)
    XNum(cnt)=days(MidXTime(cnt,1)-MidXTime(1,1));
    cnt=cnt+1;
end

Cve_05=csaps(XNum,Data(:,2)',Smth);
Cve_50=csaps(XNum,Data(:,3)',Smth);
Cve_95=csaps(XNum,Data(:,4)',Smth);
Cve_Stright=csaps(XNum,Data(:,6)',0);
Cve_n=csaps(XNum,Data(:,8)',1);

f=figure;
scatter(MidXTime,Data(:,6),'ko','filled','LineWidth',1)
hold on
plot(linspace(0,1006,1000),ppval(Cve_05,linspace(0,XNum(end),1000)),'k--','LineWidth',0.75)
plot(linspace(0,1006,1000),ppval(Cve_50,linspace(0,XNum(end),1000)),'k-','LineWidth',1)
plot(linspace(0,1006,1000),ppval(Cve_95,linspace(0,XNum(end),1000)),'k--','LineWidth',0.75)
plot(linspace(0,1006,1000),ppval(Cve_Stright,linspace(0,XNum(end),1000)),'-','LineWidth',0.5,'Color',[.7 .7 .7])
xlabel("Date")
ylabel("N")
legend(["","5% Quantile","50% Quantile","95% Quantile"],'Location','northwest')
exportgraphics(f,'Results.eps','ContentType','vector')
Mean_Est=sum(Data(:,6))/12;
Centered_Est=Data(:,6)-Mean_Est;
Mean_n=sum(Data(:,8))/12;
Centered_n=Data(:,8)-Mean_n;
A=norm(Centered_Est)/norm(Centered_n);
B=Mean_Est-Mean_n;

g=figure;
scatter(MidXTime,Data(:,6),0.01,'k')
hold on
plot(linspace(0,XNum(end),1000),ppval(Cve_50,linspace(0,XNum(end),1000)),'k-','LineWidth',1)
plot(linspace(0,XNum(end),1000),Mean_Est+A*(ppval(Cve_n,linspace(0,XNum(end),1000))-Mean_n),'k--','LineWidth',1)
xlabel("Date")
legend("","50% Quantile for N","Observed cases n (scaled)","Location","NorthWest")
exportgraphics(g,"Results2.eps",'ContentType','vector')


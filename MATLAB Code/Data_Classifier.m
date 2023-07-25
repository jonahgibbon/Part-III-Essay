tic

Forumns={'Stormfront' 'Incelsis' 'Incelsnet' 'Lookism' 'RooshV' 'Pickartist' 'Mgtow' 'Gyow' 'Kiwifarms'}';
Time='20180101';
[Pair,TotMem]=Pairs(Forumns,3/4,Time);
Ans=CombineLists(Pair,TotMem);
writematrix(Ans,strcat(Time,'.csv'))
disp(strcat("Data summary of ",Time," complete"))

toc
beep on
beep



function [MasterPairs,TotalMembers]=Pairs(Forumns,Threshold,Time)
MasterData=cell(0,2*size(Forumns,1));
MasterPairs=cell(size(Forumns,1),size(Forumns,1));
Pairs=nchoosek(1:size(Forumns,1),2);
MasterRead=cell(size(Forumns,1),1);

Counter=1;
while Counter<=size(Forumns,1)
    Progress=fprintf('LOADING IN DATA: %.2f%%',Counter*100/size(Forumns,1));
    MasterRead{Counter}=strcat(Forumns{Counter},Time,'.csv');
    Table=readtable(MasterRead{Counter,1},"Format","auto");
    MasterData{1,2*Counter-1}=Table{:,1};
    MasterData{1,2*Counter}=Table{:,2};
    fprintf(repmat('\b',1,Progress))
    Counter=Counter+1;
end


PairCounter=1;
while PairCounter<=size(Pairs,1)
    Progress=fprintf('Progress: %.3f%% \n',PairCounter*100/size(Pairs,1));
    Candidates=cell(0,2);
    Mem1Count=1;
    
    Members1=unique(MasterData{1,2*Pairs(PairCounter,1)-1});
    Members2=unique(MasterData{1,2*Pairs(PairCounter,2)-1});
    %FIND INITAL POSSIBLE PAIRS
    while Mem1Count<=size(Members1,1)
        NewProgress=fprintf('SubProgress: %.2f%%',Mem1Count/size(Members1,1)*100);
        Mem2Count=1;
        while Mem2Count<=size(Members2,1)
            if Fuzzy(Members1{Mem1Count,1},Members2{Mem2Count,1})==1
                Candidates(end+1,1)=Members1(Mem1Count,1);
                Candidates(end,2)=Members2(Mem2Count,1);
            end
            Mem2Count=Mem2Count+1;
        end
        fprintf(repmat('\b',1,NewProgress))
        Mem1Count=Mem1Count+1;
    end
    if isempty(Candidates)==0
        Counter=1;
        while Counter<=size(Candidates,1)
            Dist1=zeros(24,1);
            Dist2=zeros(24,1);

            Index=find(strcmp([MasterData{1,2*Pairs(PairCounter,1)-1}],...
                Candidates{Counter,1}));
            T=MasterData{1,2*Pairs(PairCounter,1)};
            subCounter=1;
            while subCounter<=size(Index,1)
                Dist1(hour(T(Index(subCounter,1),1))+1)=...
                    Dist1(hour(T(Index(subCounter,1),1))+1)+1;
                subCounter=subCounter+1;
            end

            Index=find(strcmp([MasterData{1,2*Pairs(PairCounter,2)-1}],...
                Candidates{Counter,2}));
            T=MasterData{1,2*Pairs(PairCounter,2)};
            subCounter=1;
            while subCounter<=size(Index,1)
                Dist2(hour(T(Index(subCounter,1),1))+1)=...
                    Dist2(hour(T(Index(subCounter,1),1))+1)+1;
                subCounter=subCounter+1;
            end
            Dist1=Dist1/sum(Dist1);
            Dist2=Dist2/sum(Dist2);
            Candidates(Counter,3)={Dist1};
            Candidates(Counter,4)={Dist2};
            AverageDist=(Dist1+Dist2)./2;

            %DISTRIBUTION CRITERION
            if Entropy(AverageDist,2)-(1/2)*Entropy(Dist1,2)-(1/2)*Entropy(Dist2,2)>Threshold
                Candidates(Counter,:)=[];
                Counter=Counter-1;
            end
            Counter=Counter+1;
        end
    else
    end
    
    if isempty(Candidates)==1
        MasterPairs{Pairs(PairCounter,1),Pairs(PairCounter,2)}=0;
    else
        MasterPairs{Pairs(PairCounter,1),Pairs(PairCounter,2)}=Candidates;
    end
    fprintf(repmat('\b',1,Progress))
    PairCounter=PairCounter+1;
end
TotalMembers=zeros(size(Forumns,1),1);
Count=1;
while Count<=size(Forumns,1)
    Mems=unique(MasterData{1,2*Count-1});
    TotalMembers(Count,1)=size(Mems,1);
    Count=Count+1;
end
end

function CompleteData = CombineLists(MasterPairs,TotalMembers)

CompleteData=zeros(2^size(MasterPairs,1)-1,size(MasterPairs,1)+1);
DataCnt=0;
MstCnt=size(MasterPairs,1);
while MstCnt>=3
    Comb=nchoosek(1:size(MasterPairs,1),MstCnt);
    SubCnt=size(Comb,1);
    while SubCnt>=1
        CurComb=Comb(SubCnt,:);
        if isa(MasterPairs{CurComb(1),CurComb(2)},'cell')==1
            T=MasterPairs{CurComb(1),CurComb(2)};
            PossNames=T(:,1:2);
            PossDist=T(:,3:4);
            IntCnt=2;
            while IntCnt<=MstCnt-1
                if isa(MasterPairs{CurComb(IntCnt),CurComb(IntCnt+1)},'cell')==1
                    T=MasterPairs{CurComb(IntCnt),CurComb(IntCnt+1)};
                    TrialNames=T(:,1:2);
                    TrialDist=T(:,3:4);
                    AnCnt1=1;
                    while AnCnt1<=size(PossNames,1)
                        AnCnt2=1;
                        while AnCnt2<=size(TrialNames,1)
                            if Fuzzy(PossNames{AnCnt1,IntCnt},TrialNames{AnCnt2,1})==1
                                PossNames{AnCnt1,IntCnt+1}=TrialNames{AnCnt2,1};
                                PossDist{AnCnt1,IntCnt+1}=TrialDist{AnCnt2,1};
                                break
                            else
                            end
                            AnCnt2=AnCnt2+1;
                        end
                        AnCnt1=AnCnt1+1;
                    end
                    if size(PossNames,2)==IntCnt
                        PossNames=cell(0,0);
                        PossDist=cell(0,0);
                        break
                    else
                        Cnt=1;
                        while Cnt<=size(PossNames,1)
                            if size(PossDist{Cnt,IntCnt+1},1)~=24
                                PossNames(Cnt,:)=[];
                                PossDist(Cnt,:)=[];
                                Cnt=Cnt-1;
                            end
                            Cnt=Cnt+1;
                        end
                        if size(PossNames,1)==0
                            PossNames=cell(0,0);
                            PossDist=cell(0,0);
                            break
                        end
                    end                    
                else
                    PossNames=cell(0,0);
                    PossDist=cell(0,0);
                    break
                end
                IntCnt=IntCnt+1;
            end
        else
            PossNames=cell(0,0);
            PossDist=cell(0,0);
        end
        DataCnt=DataCnt+1;
        Count=1;
        while Count<=size(MasterPairs,1)
            if ismember(Count,CurComb)==1
                CompleteData(DataCnt,Count)=1;
            end
            Count=Count+1;
        end
        CompleteData(DataCnt,size(MasterPairs,1)+1)=size(PossNames,1);
        SubCnt=SubCnt-1;
    end
    MstCnt=MstCnt-1;
end

Index=nchoosek(1:size(MasterPairs,1),2);
MstCnt=size(Index,1);
while MstCnt>=1
    DataCnt=DataCnt+1;
    Comb1=Index(MstCnt,1);
    Comb2=Index(MstCnt,2);
    CompleteData(DataCnt,Comb1)=1;
    CompleteData(DataCnt,Comb2)=1;
    if isa(MasterPairs(Comb1,Comb2),'cell')==1
        CompleteData(DataCnt,size(MasterPairs,1)+1)=size(MasterPairs{Comb1,Comb2},1);
    end
    MstCnt=MstCnt-1;
end
MstCnt=size(MasterPairs,1);
while MstCnt>=1
    DataCnt=DataCnt+1;
    CompleteData(DataCnt,MstCnt)=1;
    CompleteData(DataCnt,size(MasterPairs,1)+1)=TotalMembers(MstCnt,1);
    MstCnt=MstCnt-1;
end

%CLEAN UP OVERCOUNT PROBLEM
MstCnt=1;
while MstCnt<=size(CompleteData,1)
    a=CompleteData(MstCnt,1:size(MasterPairs,1));
    SubCnt=MstCnt+1;
    while SubCnt<=size(CompleteData,1)
        b=CompleteData(SubCnt,1:size(MasterPairs,1));
        if compare(a,b)==1
            CompleteData(SubCnt,size(MasterPairs,1)+1)=...
                CompleteData(SubCnt,size(MasterPairs,1)+1)-...
                CompleteData(MstCnt,size(MasterPairs,1)+1);
        end
        SubCnt=SubCnt+1;
    end
    MstCnt=MstCnt+1;
end
CompleteData=flipud(CompleteData);

Counter=1;
while Counter<=size(CompleteData,1)
    if CompleteData(Counter,size(MasterPairs,1)+1)<0
        CompleteData(Counter,size(MasterPairs,1)+1)=0;
    end
    Counter=Counter+1;
end
end
function answer = compare(a,b)
Counter=1;
answer=1;
while Counter<=size(a,2)
    if b(1,Counter)==1
        if a(1,Counter)==1
        else
            answer=0;
        end
    else
    end
    Counter=Counter+1;
end
end
function outcome = Fuzzy(a,b)
if abs(size(a,2)-size(b,2))>=2
    outcome=0;
elseif abs(size(a,2)-size(b,2))==1
    if size(a,2)<size(b,2)
        small=a;
        big=b;
    else
        small=b;
        big=a;
    end
    n=1;
    ProblemFlag=0;
    while n<=size(big,2)
        Check=eraseBetween(big,n,n);
        if strcmp(Check,small)==0
        else
            ProblemFlag=1;
            break
        end
        n=n+1;
    end
    if ProblemFlag==0
        outcome=0;
    else
        outcome=1;
    end
else
    n=1;
    ProblemFlag=0;
    while n<=size(a,2)
        Check1=eraseBetween(a,n,n);
        Check2=eraseBetween(b,n,n);
        if strcmp(Check1,Check2)==0
        else
            ProblemFlag=1;
            break
        end
        n=n+1;
    end
    if ProblemFlag==0
        outcome=0;
    else 
        outcome=1;
    end
end
end
function answer = Entropy(a,base)
Counter=1;
answer=0;
while Counter<=size(a,1)
    if a(Counter)==0
    else
        answer=answer-a(Counter)*log(a(Counter))/log(base);
    end 
    Counter=Counter+1;
end
Counter=1;
while Counter<=size(Data,1)

    if Data(Counter,end)==0
        Data(Counter,:)=[];
        Counter=Counter-1;
    end
    Counter=Counter+1;
end
end
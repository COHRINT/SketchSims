import numpy as np; 
import scipy.stats as stats
import matplotlib.pyplot as plt; 

#a = np.load('../data/simHARPS_Test.npy').item(); 

#print(a['tag'])

def check():

    #hum = np.load("../../../../../mnt/d/SimHARPS/simHARPS_Human_nom.npy").item(); 
    #hum = np.load("../../../../../mnt/d/SimHARPS/simHARPS_Nonhuman_nom.npy").item(); 

    #hum = np.load('../data/simHARPS_Nom_C_p1.npy',allow_pickle=True).item(); 

   # hum = np.load('../data/simHARPS_Nom_C_p5.npy',allow_pickle=True).item(); 


    #hum = np.load('../data/simHARPS_Nom_C_1.npy',allow_pickle=True).item(); 

    #hum = np.load('../data/simHARPS_Nom_C_2.npy',allow_pickle=True).item(); 
    #hum = np.load('../data/simHARPS_Nom_C_5.npy',allow_pickle=True).item(); 
    print("The Best option for Exploration: 1")

    hum = np.load('../data/simHARPS_Nom_C_10.npy',allow_pickle=True).item(); 

    allTimes = []; 
    allCatchTimes = []; 

    for sim in hum['sims']:
        allTimes.append(sim['TotalTime']); 
        if(sim['TotalTime'] < 300):
            allCatchTimes.append(sim['TotalTime']); 

    print("Average Time: {}".format(np.mean(allTimes)))
    print("Average Catch Time: {}".format(np.mean(allCatchTimes))); 
    print("Capture Standard Dev: {}".format(np.std(allCatchTimes))); 
    print("Ratio of Capture: {}".format(len(allCatchTimes)/len(allTimes)));

def poisExtract():
    allDat = []; 

    for po in range(0,6):
        print("Pois_Mean: {}".format(po)); 
        allCatchTimes = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/Pois_{}/Pois_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            if(data['Captured'] == True):
                allCatchTimes.append(data['TotalTime']); 
            del data
        allDat.append(allCatchTimes); 
    np.save('../data/pois_small.npy',allDat); 

def poisCheck():

    plt.figure(); 
    data = np.load('../data/pois_small.npy',allow_pickle=True)
    allAves = []; 
    allSD = []; 
    allRatio = [];  
    for d in data:
        allAves.append(np.mean(d)); 
        allSD.append(np.std(d)); 
        allRatio.append(len(d)/100); 

    x = [i for i in range(3,9)]; 
    plt.plot(x,allRatio); 
    plt.scatter(x,allRatio,s=50,marker='*',color='black',label='Tested Values'); 
    plt.ylabel('Ratio of Captures to Total Runs'); 
    plt.xlabel('Poisson Mean'); 
    plt.title("Effect of Varying Poisson Means on POMDP Performance"); 
    plt.legend(); 
    plt.savefig('../figs/poisson_graph.png'); 

    plt.figure(); 
    allTests = np.zeros(shape=(6,6)); 

    allSigX = []; 
    allSigY = []; 
    for i in range(0,6):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
            if(allTests[i,j] < 0.05):
                allSigX.append(j); 
                allSigY.append(i); 
        for j in range(i,6):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4,5,6],[3,4,5,6,7,8]); 
    plt.xticks([0,1,2,3,4,5,6],[3,4,5,6,7,8]); 
    plt.colorbar(); 

    for i in range(0,6):
        for j in range(0,i):
            if(allTests[i,j] != np.nan):
                tmp = str(allTests[i,j]); 
                tmp = tmp[0:5];
                if(allTests[i,j] < 0.05):
                    tmp = tmp+'*'; 
                    if(allTests[i,j] < 0.01):
                        tmp = tmp+'*'; 
                        if(allTests[i,j] < 0.001):
                            tmp = tmp+'*'; 

                plt.text(j,i+0.25,tmp,fontsize=12,verticalalignment = 'center',horizontalalignment='center',color='red'); 

    plt.scatter(allSigX,allSigY,marker='*',s=50, color='red',label='Significant p<0.05')
    plt.axis('tight'); 
    plt.xlabel("Tested Values"); 
    plt.ylabel("Tested Values")
    plt.title("Binomial Test Significance of Poisson Means"); 
    plt.legend();
    plt.savefig('../figs/poisson_sig.png'); 
    #plt.show();


def amultExtract():
    allDat = []; 

    mults = ['1p5','2','3','4','5','10']

    for po in mults:
        print("Area Multiplier: {}".format(po)); 
        allCatchTimes = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/amult_{}/amult_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            if(data['Captured'] == True):
                allCatchTimes.append(data['TotalTime']); 
            del data
        allDat.append(allCatchTimes); 
    np.save('../data/amult_small.npy',allDat); 

def amultCheck():

    plt.figure(); 
    data = np.load('../data/amult_small.npy',allow_pickle=True)
    allAves = []; 
    allSD = []; 
    allRatio = [];  
    for d in data:
        allAves.append(np.mean(d)); 
        allSD.append(np.std(d)); 
        allRatio.append(len(d)/100); 

    x = [1.5,2,3,4,5,10]; 
    plt.plot(x,allRatio); 
    plt.scatter(x,allRatio,s=50,marker='*',color='black', label='Tested Values'); 
    plt.ylabel('Catch Ratio'); 
    plt.xlabel('Area Mutliplier'); 
    plt.title("Effect of Varying Near Area Multiplier on POMDP Performance"); 
    plt.legend(); 
    plt.savefig('../figs/areaMult_graph.png'); 

    plt.figure(); 
    allSigX = []; 
    allSigY = []; 
    allTests = np.zeros(shape=(6,6)); 
    for i in range(0,6):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
            if(allTests[i,j] < 0.05):
                allSigX.append(j); 
                allSigY.append(i); 
        for j in range(i,6):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 



    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4,5,6],[1.5,2,3,4,5,10]); 
    plt.xticks([0,1,2,3,4,5,6],[1.5,2,3,4,5,10]); 
    plt.colorbar(); 

    for i in range(0,6):
        for j in range(0,i):
            if(allTests[i,j] != np.nan):
                tmp = str(allTests[i,j]); 
                tmp = tmp[0:5];
                if(allTests[i,j] < 0.05):
                    tmp = tmp+'*'; 
                    if(allTests[i,j] < 0.01):
                        tmp = tmp+'*'; 
                        if(allTests[i,j] < 0.001):
                            tmp = tmp+'*'; 

                plt.text(j,i+0.25,tmp,fontsize=12,verticalalignment = 'center',horizontalalignment='center',color='red'); 

    plt.scatter(allSigX,allSigY,marker='*',s=50, color='red',label='Significant p<0.05')
    plt.xlabel("Tested Values"); 
    plt.ylabel("Tested Values")
    plt.axis('tight'); 
    plt.title("Binomial Significance of Near Area Multipliers"); 
    plt.legend();
    plt.savefig('../figs/areaMult_sig.png');


def sketchRateExtract():
    allDat = []; 

    mults = ['15s','30s','60s','120s','inf']

    for po in mults:
        print("Sketch Rate: {}".format(po)); 
        allCatchTimes = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/sketchRate_{}/sketchRate_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            if(data['Captured'] == True):
                allCatchTimes.append(data['TotalTime']); 
            del data
        allDat.append(allCatchTimes); 
    np.save('../data/sketchRate_small.npy',allDat); 


def sketchRateCheck():
    plt.figure(); 
    data = np.load('../data/sketchRate_small.npy',allow_pickle=True)
    allAves = []; 
    allSD = []; 
    allRatio = [];  
    for d in data:
        allAves.append(np.mean(d)); 
        allSD.append(np.std(d)); 
        allRatio.append(len(d)/100); 

    #x = [1.5,2,3,4,5,10];
    x = [15,30,60,120,240];  
    plt.plot(x,allRatio);
    plt.scatter(x,allRatio,s=50,marker='*',color='black', label='Tested Values'); 
    plt.xticks([15,30,60,120,240],[15,30,60,120,'inf']); 
    plt.ylabel('Catch Ratio'); 
    plt.xlabel('Sketch Rate (s)'); 
    plt.title("Effect of Varying Sketch Rate on POMDP Performance"); 
    plt.legend(); 
    plt.savefig('../figs/sketchRate_graph.png'); 

    plt.figure(); 
    allSigX = []; 
    allSigY = []; 
    allTests = np.zeros(shape=(5,5)); 
    for i in range(0,5):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
            if(allTests[i,j] < 0.05):
                allSigX.append(j); 
                allSigY.append(i); 
        for j in range(i,5):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4],[15,30,60,120,'inf']); 
    plt.xticks([0,1,2,3,4],[15,30,60,120,'inf']); 
    plt.colorbar(); 
    for i in range(0,5):
        for j in range(0,i):
            if(allTests[i,j] != np.nan):
                tmp = str(allTests[i,j]); 
                tmp = tmp[0:5];
                if(allTests[i,j] < 0.001):
                    tmp = "<0.001"; 
                if(allTests[i,j] < 0.05):
                    tmp = tmp+'*'; 
                    if(allTests[i,j] < 0.01):
                        tmp = tmp+'*'; 
                        if(allTests[i,j] < 0.001):
                            tmp = tmp+'*'; 

                plt.text(j,i+0.25,tmp,fontsize=10,verticalalignment = 'center',horizontalalignment='center',color='red'); 
    plt.scatter(allSigX,allSigY,marker='*',s=50, color='red',label='Significant p<0.05')
    plt.xlabel("Tested Values"); 
    plt.ylabel("Tested Values")
    plt.axis('tight'); 
    plt.title("Binomial Significance of Sketch Rate"); 
    plt.legend();
    plt.savefig('../figs/sketchRate_sig.png'); 


def accuracyDataExtract():

    mults = {}; 
    labs = ['3','5','7','9','95']; 
    for l in labs:
        s = {}; 
        for l2 in labs:
            suma = 0; 
            for i in range(0,50):
                #data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
                data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
            
                if(data['Captured'] == True):
                    suma += 1/50; 

            s[l2] = suma;  
        mults[l] = s; 
    np.save('../data/acc_all.npy',mults); 

def availabilityDataExtract():

    mults = {}; 
    labs = ['3','5','7','9','95']; 
    for l in labs:
        print("Label: {}".format(l)); 
        s = {}; 
        for l2 in labs:
            suma = 0; 
            for i in range(0,50):
                #data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
                data = np.load('../data/avail_p{}_p{}/avail_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
            
                if(data['Captured'] == True):
                    suma += 1/50; 

            s[l2] = suma;  
        mults[l] = s; 
    np.save('../data/avail_all.npy',mults); 

def accuracyDataCheck():
    data = np.load('../data/acc_all.npy',allow_pickle=True).item();  
    #print(data['9'])
    x = []; 

    keySet = ['3','5','7','9','95']
    colors = []; 
    for ac in keySet:
        tmp = []; 
        for ac2 in keySet:
            tmp.append(data[ac][ac2]);  
        x.append(tmp); 
    fig,ax = plt.subplots(); 

    im = ax.imshow(x,origin='lower left'); 
    fig.colorbar(im,ax=ax);  
    ax.set_ylabel("Actual"); 
    ax.set_xlabel("Assumed"); 
    ax.set_xticks([0,1,2,3,4]); 
    ax.set_yticks([0,1,2,3,4]); 
    ax.set_xticklabels([.3,.5,.7,.9,.95]); 
    ax.set_yticklabels([.3,.5,.7,.9,.95]); 
    plt.title("Capture Rates for Actual vs. Assumed Accuracy"); 
    plt.savefig('../figs/acc_data.png'); 
   

    fig,ax = plt.subplots(); 
    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[i][j]/5; 
        tmp.append(suma); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_xlabel('Actual Accuracy'); 
    ax.set_ylabel("Capture Rate"); 
    plt.title("Average effect of Human Accuracy on Capture Rate"); 
    plt.legend(); 
    plt.savefig('../figs/acc_true.png')

    fig,ax = plt.subplots(); 
    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[j][i]/5; 
        tmp.append(suma); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_ylabel("Capture Rate"); 
    ax.set_xlabel("Assumed Accuracy"); 
    plt.title("Average Effect of Assumed Accuracy on Capture Rate")
    plt.legend(); 
    plt.savefig('../figs/acc_think.png'); 

    fig,ax = plt.subplots(); 
    tmp = []; 
    for i in range(0,5):
        tmp.append(x[i][i]); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_xlabel("Matched Accuracy"); 
    ax.set_ylabel("Catch Rate"); 
    plt.legend(); 
    plt.title("Effect of Matched Accuracy on Capture Rate"); 
    plt.savefig('../figs/acc_matched.png'); 



    plt.figure(); 
    allSigX = []; 
    allSigY = []; 
    allTests = np.zeros(shape=(5,5)); 
    for i in range(0,5):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(tmp[i]*100,n=100,p=tmp[j]); 
            if(allTests[i,j] < 0.05):
                allSigX.append(j); 
                allSigY.append(i); 
        for j in range(i,5):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4],[.3,.5,.7,.9,.95]); 
    plt.xticks([0,1,2,3,4],[.3,.5,.7,.9,.95]); 
    plt.colorbar(); 
    for i in range(0,5):
        for j in range(0,i):
            if(allTests[i,j] != np.nan):
                tmp = str(allTests[i,j]); 
                tmp = tmp[0:5];
                if(allTests[i,j] < 0.001):
                    tmp = "<0.001"; 
                if(allTests[i,j] < 0.05):
                    tmp = tmp+'*'; 
                    if(allTests[i,j] < 0.01):
                        tmp = tmp+'*'; 
                        if(allTests[i,j] < 0.001):
                            tmp = tmp+'*'; 

                plt.text(j,i+0.25,tmp,fontsize=10,verticalalignment = 'center',horizontalalignment='center',color='red'); 
    plt.scatter(allSigX,allSigY,marker='*',s=50, color='red',label='Significant p<0.05')
    plt.xlabel("Tested Values"); 
    plt.ylabel("Tested Values")
    plt.axis('tight'); 
    plt.title("Binomial Significance of Matched Accuracy"); 
    plt.legend();
    plt.savefig('../figs/acc_matched_sig.png'); 


def availabilityDataCheck():
    data = np.load('../data/avail_all.npy',allow_pickle=True).item();  
    #print(data['9'])
    x = []; 

    keySet = ['3','5','7','9','95']
    colors = []; 
    for ac in keySet:
        tmp = []; 
        for ac2 in keySet:
            tmp.append(data[ac][ac2]);  
        x.append(tmp); 
    fig,ax = plt.subplots(); 

    im = ax.imshow(x,origin='lower left'); 
    fig.colorbar(im,ax=ax);  
    ax.set_ylabel("Actual"); 
    ax.set_xlabel("Assumed"); 
    ax.set_xticks([0,1,2,3,4]); 
    ax.set_yticks([0,1,2,3,4]); 
    ax.set_xticklabels([.3,.5,.7,.9,.95]); 
    ax.set_yticklabels([.3,.5,.7,.9,.95]); 
    plt.title("Capture Rates for Actual vs. Assumed Availability"); 
    plt.savefig('../figs/avail_data.png'); 
   

    fig,ax = plt.subplots(); 
    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[i][j]/5; 
        tmp.append(suma); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_xlabel('Actual Availability'); 
    ax.set_ylabel("Capture Rate"); 
    plt.title("Average effect of Human Availability on Capture Rate"); 
    plt.legend(); 
    plt.savefig('../figs/avail_true.png')

    fig,ax = plt.subplots(); 
    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[j][i]/5; 
        tmp.append(suma); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_ylabel("Capture Rate"); 
    ax.set_xlabel("Assumed Availability"); 
    plt.title("Average Effect of Assumed Availability on Capture Rate")
    plt.legend(); 
    plt.savefig('../figs/avail_think.png'); 

    # fig,ax = plt.subplots(); 
    # tmp = []; 
    # for i in range(0,5):
    #     tmp.append(x[i][i]); 
    # ax.plot(rangX,tmp); 
    # ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    # ax.set_xlabel("Matched Availability"); 
    # ax.set_ylabel("Catch Rate"); 
    # plt.legend(); 
    # plt.title("Effect of Matched Availability on Capture Rate"); 
    # plt.savefig('../figs/avail_matched.png'); 



    # plt.figure(); 
    # allSigX = []; 
    # allSigY = []; 
    # allTests = np.zeros(shape=(5,5)); 
    # for i in range(0,5):
    #     for j in range(0,i):
    #         allTests[i,j] = stats.binom_test(tmp[i]*100,n=100,p=tmp[j]); 
    #         if(allTests[i,j] < 0.05):
    #             allSigX.append(j); 
    #             allSigY.append(i); 
    #     for j in range(i,5):
    #         allTests[i,j] = np.nan; 

    #     allTests[i,i] = np.nan; 
    # plt.imshow(allTests,vmax=1.0,vmin=0);
    # plt.yticks([0,1,2,3,4],[.3,.5,.7,.9,.95]); 
    # plt.xticks([0,1,2,3,4],[.3,.5,.7,.9,.95]); 
    # plt.colorbar(); 
    # for i in range(0,5):
    #     for j in range(0,i):
    #         if(allTests[i,j] != np.nan):
    #             tmp = str(allTests[i,j]); 
    #             tmp = tmp[0:5];
    #             if(allTests[i,j] < 0.001):
    #                 tmp = "<0.001"; 
    #             if(allTests[i,j] < 0.05):
    #                 tmp = tmp+'*'; 
    #                 if(allTests[i,j] < 0.01):
    #                     tmp = tmp+'*'; 
    #                     if(allTests[i,j] < 0.001):
    #                         tmp = tmp+'*'; 

    #             plt.text(j,i+0.25,tmp,fontsize=10,verticalalignment = 'center',horizontalalignment='center',color='red'); 
    # plt.scatter(allSigX,allSigY,marker='*',s=50, color='red',label='Significant p<0.05')
    # plt.xlabel("Tested Values"); 
    # plt.ylabel("Tested Values")
    # plt.axis('tight'); 
    # plt.title("Binomial Significance of Matched Availability"); 
    # plt.legend();
    # plt.savefig('../figs/avail_matched_sig.png'); 


def predictiveObsPlanningExtract():
    allDat = []; 

    mults = ['human_blindPlan','human_treePlan']

    for po in mults:
        print("Plan: {}".format(po)); 
        allCatchTimes = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/{}/{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            if(data['Captured'] == True):
                allCatchTimes.append(data['TotalTime']); 
            del data
        allDat.append(allCatchTimes); 
    np.save('../data/planningType_small.npy',allDat); 

def predictiveObsPlanningCheck():

    plt.figure(); 
    data = np.load('../data/planningType_small.npy',allow_pickle=True)
    allAves = []; 
    allSD = []; 
    allRatio = [];  
    for d in data:
        allAves.append(np.mean(d)); 
        allSD.append(np.std(d)); 
        allRatio.append(len(d)/100); 

    #x = [1.5,2,3,4,5,10];
    #x = [15,30,60,120,240];  
    #plt.plot(x,allRatio);
    #plt.scatter(x,allRatio,s=50,marker='*',color='black'); 
    #plt.xticks([15,30,60,120,240],[15,30,60,120,'inf']); 
    plt.bar([0,1],allRatio,color=['red','blue'],edgecolor='black',linewidth=2); 
    plt.ylabel('Catch Ratio'); 
    #plt.xlabel('Sketch Rate (s)'); 
    plt.xticks([0,1],['Blind','Predictive']); 
    
    


    test = stats.binom_test(allRatio[1]*100,n=100,p=allRatio[0]); 

    #print("Binomial Significance of Predictive Planning: {}".format(test));
    plt.title("Significance of Predictive Tree Planning: {0:.2f}".format(test)); 
    plt.savefig('../figs/predictive_sig.png'); 
    #plt.show();

if __name__ == '__main__':
    #poisExtract(); 
    poisCheck();
    #amultExtract(); 
    amultCheck(); 

    #sketchRateExtract(); 
    sketchRateCheck();

    #accuracyDataExtract();  
    accuracyDataCheck();

    #availabilityDataExtract(); 
    availabilityDataCheck(); 

    #predictiveObsPlanningExtract(); 
    predictiveObsPlanningCheck(); 

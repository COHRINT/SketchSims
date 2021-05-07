import numpy as np; 
import scipy.stats as stats
import matplotlib.pyplot as plt; 

import matplotlib.image as mpimg
import matplotlib.animation as animation


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
    plt.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    plt.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    plt.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
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
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
    plt.title("Average Effect of Assumed Availability on Capture Rate")
    plt.legend(); 
    plt.savefig('../figs/avail_think.png'); 

    fig,ax = plt.subplots(); 
    tmp = []; 
    for i in range(0,5):
        tmp.append(x[i][i]); 
    ax.plot(rangX,tmp); 
    ax.scatter(rangX,tmp,s=50,marker='*',color='black', label='Tested Values'); 
    ax.set_xlabel("Matched Availability"); 
    ax.set_ylabel("Catch Rate"); 
    ax.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
    plt.legend(); 
    plt.title("Effect of Matched Availability on Capture Rate"); 
    plt.savefig('../figs/avail_matched.png'); 



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
    plt.title("Binomial Significance of Matched Availability"); 
    plt.legend();
    plt.savefig('../figs/avail_matched_sig.png'); 


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
    plt.text(0,allRatio[0]+0.012,str(allRatio[0]),verticalalignment = 'center',horizontalalignment = 'center'); 
    plt.text(1,allRatio[1]+0.012,str(allRatio[1]),verticalalignment = 'center',horizontalalignment = 'center'); 
    
    plt.ylabel('Catch Ratio'); 
    #plt.xlabel('Sketch Rate (s)'); 
    plt.xticks([0,1],['Blind','Predictive']); 
    
    


    test = stats.binom_test(allRatio[1]*100,n=100,p=allRatio[0]); 

    #print("Binomial Significance of Predictive Planning: {}".format(test));
    plt.title("Significance of Predictive Tree Planning: {0:.2f}".format(test)); 
    plt.savefig('../figs/predictive_sig.png'); 
    #plt.show();

def humanDataExtract():
    allDat = []; 

    print("Extracting data for human test"); 

    mults = ['Human_Long','NonHuman_Long']

    for po in mults:
        print("Plan: {}".format(po)); 
        allCatchTimes = []; 
        for i in range(0,250):
            #print(i); 
            data = np.load('../data/{}/{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            if(data['Captured'] == True):
                allCatchTimes.append(data['TotalTime']); 
            del data
        allDat.append(allCatchTimes); 
    np.save('../data/human_nonhuman_large.npy',allDat);


def humanDataCheck(show=False):

    plt.figure(); 
    data = np.load('../data/human_nonhuman_large.npy',allow_pickle=True)
    allAves = []; 
    allSD = []; 
    allRatio = [];  
    for d in data:
        allAves.append(np.mean(d)); 
        allSD.append(np.std(d)); 
        allRatio.append(len(d)/250); 

    #x = [1.5,2,3,4,5,10];
    #x = [15,30,60,120,240];  
    #plt.plot(x,allRatio);
    #plt.scatter(x,allRatio,s=50,marker='*',color='black'); 
    #plt.xticks([15,30,60,120,240],[15,30,60,120,'inf']); 
    plt.bar([0,1],allRatio,color=['blue','red'],edgecolor='black',linewidth=2); 
    plt.text(0,allRatio[0]+0.012,str(allRatio[0]),verticalalignment = 'center',horizontalalignment = 'center'); 
    plt.text(1,allRatio[1]+0.012,str(allRatio[1]),verticalalignment = 'center',horizontalalignment = 'center'); 
    
    plt.ylabel('Catch Ratio'); 
    #plt.xlabel('Sketch Rate (s)'); 
    plt.xticks([0,1],['Human','Nonhuman']); 
    
    


    test = stats.binom_test(allRatio[0]*250,n=250,p=allRatio[1]); 

    #print("Binomial Significance of Human Involvement: {}".format(test));
    if(test < 0.001):
        test = 'p<0.001'; 
    plt.title("Significance of Human Involvement: {}".format(test)); 
    if(show):
        plt.show()
    else:
        plt.savefig('../figs/human_sig.png'); 


def predictiveStateObsExtract():
    allDat = []; 

    mults = ['human_blindPlan','human_treePlan']



    for po in mults:
        print("Plan: {}".format(po)); 
        allStateObs = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/{}/{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            # if(data['Captured'] == True):
            #     allCatchTimes.append(data['TotalTime']); 
            # del data
            allStateObs.append({'States':data['States'],'Obs':data['Drone_Obs'], 'Times':data['DecisionTimes'],"Captured":data['Captured']}); 
        allDat.append(allStateObs); 
    np.save('../data/planningType_stateObs.npy',allDat); 

def predictiveSlipAways(show=False):
    #plt.figure(); 
    data = np.load('../data/planningType_stateObs.npy',allow_pickle=True)



    allCapDiffs= [[],[]] 
    perCap = [0,0]; 
    for i in range(0,len(data)):
        for j in range(0,len(data[i])):
            flag = False
            if(data[i][j]['Captured']):
                perCap[i] += .01; 
            for k in range(0,min(599,len(data[i][j]['Obs'])-5)):
                if(data[i][j]['Obs'][k] == 'Detect'):
                    if(data[i][j]['Captured'] and len(data[i][j]['Obs'])-k < 600):
                        dur =  min(599,len(data[i][j]['Obs'])-k); 
                        #capTimes[i,dur] += 1; 
                        allCapDiffs[i].append(dur)
                        flag = True; 

                # if(flag):
                #     break; 
                    # elif(data[i][j]['Times'][-1] >= 600):
                    #     capTimes[i,600] += 1; 

                    # if(len(data[i][j]['Obs'])-k < 600):
                    #     dur =  len(data[i][j]['Obs'])-k; 
                    #     capTimes[i,dur] += 1; 

    #plt.hist(allCapDiffs[0],color='red',alpha=0.3,bins=15,density=True); 
    #plt.hist(allCapDiffs[1],color='blue',alpha=0.3,bins=15,density=True); 

    fig,ax1 = plt.subplots(); 
    ax2 = ax1.twinx(); 


    heights,edges = np.histogram(allCapDiffs[0], bins=15)
    binCenters = (edges[:-1] + edges[1:])/2

    # norm the heights
    heights = heights/heights.sum()
    cdf = heights.cumsum()
    

    ax1.plot(binCenters, cdf, color='red',label='Blind CDF')
    ax2.bar(binCenters, heights, color='red',alpha=0.3, width=38, label='Blind Pursuit Time')

    heights,edges = np.histogram(allCapDiffs[1], bins=15)
    binCenters = (edges[:-1] + edges[1:])/2

    # norm the heights
    heights = heights/heights.sum()
    cdf = heights.cumsum()


    ax1.plot(binCenters, cdf, color='blue', label = 'Predictive CDF')
    ax2.bar(binCenters, heights, color='blue',alpha=0.3, width = 38, label='Predictive Pursuit Time')
    ax1.legend(loc='upper right'); 
    ax2.legend(loc='upper left'); 
    ax2.set_ylim([0,.30]); 
    ax1.set_ylim([0,1.2]);
    ax1.axhline(1,linestyle='--',color='black');  
    ax1.set_ylabel("Cummulative Percentiles")
    ax2.set_ylabel("Histogram Percentiles")
    ax1.set_xlabel("Pursuit Time (s): Capture - Detection")
    plt.title("Pursuit Times of Blind and Predictive Planning")
    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/predictive_pursuit.png'); 

def accQuestionsExtract():
    mults = {}; 
    labs = ['3','5','7','9','95']; 
    for l in labs:
        allActions = []; 
        for i in range(0,50):
            #data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
            data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l,l,l,i), allow_pickle=True).item(); 
        
            allActions.append(data['Actions']); 

 
        mults[l] = allActions; 
    np.save('../data/acc_matched_quests.npy',mults); 

def availQuestionsExtract():
    mults = {}; 
    labs = ['3','5','7','9','95']; 
    for l in labs:
        allActions = []; 
        for i in range(0,50):
            #data = np.load('../data/acc_p{}_p{}/acc_p{}_p{}_{}.npy'.format(l,l2,l,l2,i), allow_pickle=True).item(); 
            data = np.load('../data/avail_p{}_p{}/avail_p{}_p{}_{}.npy'.format(l,l,l,l,i), allow_pickle=True).item(); 
        
            allActions.append(data['Actions']); 

 
        mults[l] = allActions; 
    np.save('../data/avail_matched_quests.npy',mults); 


def accQuestionsCheck(show=False):
    data = np.load('../data/acc_matched_quests.npy',allow_pickle=True).item();  
    plt.figure(); 

    keySet = ['3','5','7','9','95']

    #for ac in keySet:

    numQuests = {}; 
    numActs = {}; 

    numInside = {}; 
    numNear = {}; 
    for ac in keySet:
        total = 0; 
        totalActs = 0; 
        totalNear = 0; 
        totalInside = 0; 
        for run in data[ac]:
            for act in run:
                if(act[1][0] is not None):
                    if(act[1][1] == 'Near'):
                        totalNear += 1; 
                    elif(act[1][1] == 'Inside'):
                        totalInside += 1; 
                    total += 1; 
                totalActs += 1; 
        numQuests[ac] = total; 
        numActs[ac] = totalActs; 
        numInside[ac] = totalInside; 
        numNear[ac] = totalNear

    for ac in keySet:
        print("Accuracy: {}, Percent Questions: {}".format(ac,numQuests[ac]/numActs[ac])); 
        #print("Accuracy: {}, Per Near: {}, Per Inside: {}".format(ac,numNear[ac]/numQuests[ac], numInside[ac]/numQuests[ac])); 
       # print("Accuracy: {}, Per Close: {}".format(ac,numNear[ac]/numQuests[ac]+ numInside[ac]/numQuests[ac])); 

    allQuestRatios = []; 
    for ac in keySet:
        allQuestRatios.append(numQuests[ac]/numActs[ac]); 

    rangX = [.3,.5,.7,.9,.95];
    plt.plot(rangX,allQuestRatios,color='orange'); 
  

    plt.scatter(rangX,allQuestRatios,s=50,marker='*',color='black', label='Tested Values'); 
    plt.xlabel("Matched Accuracy"); 
    plt.ylabel("Percentage of Actions which include Questions"); 
    #plt.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
    plt.legend(); 
    plt.title("Effect of Matched Accuracy on Number of Questions"); 
    plt.ylim([.5,1])


    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/acc_quests.png'); 

   # print(numQuests); 


def availQuestionsCheck(show=False):
    data = np.load('../data/avail_matched_quests.npy',allow_pickle=True).item();  

    plt.figure(); 

    keySet = ['3','5','7','9','95']

    #for ac in keySet:

    numQuests = {}; 
    numActs = {}; 

    numInside = {}; 
    numNear = {}; 
    for ac in keySet:
        total = 0; 
        totalActs = 0; 
        totalNear = 0; 
        totalInside = 0; 
        for run in data[ac]:
            for act in run:
                if(act[1][0] is not None):
                    if(act[1][1] == 'Near'):
                        totalNear += 1; 
                    elif(act[1][1] == 'Inside'):
                        totalInside += 1; 
                    total += 1; 
                totalActs += 1; 
        numQuests[ac] = total; 
        numActs[ac] = totalActs; 
        numInside[ac] = totalInside; 
        numNear[ac] = totalNear

    for ac in keySet:
        print("Availability: {}, Percent Questions: {}".format(ac,numQuests[ac]/numActs[ac])); 
        #print("Availability: {}, Per Near: {}, Per Inside: {}".format(ac,numNear[ac]/numQuests[ac], numInside[ac]/numQuests[ac])); 
        #print("Availability: {}, Per Close: {}".format(ac,numNear[ac]/numQuests[ac]+ numInside[ac]/numQuests[ac])); 

    allQuestRatios = []; 
    for ac in keySet:
        allQuestRatios.append(numQuests[ac]/numActs[ac]); 

    rangX = [.3,.5,.7,.9,.95];
    plt.plot(rangX,allQuestRatios,color='orange'); 
  

    plt.scatter(rangX,allQuestRatios,s=50,marker='*',color='black', label='Tested Values'); 
    plt.xlabel("Matched Availability"); 
    plt.ylabel("Percentage of Actions which include Questions"); 
    #plt.axhline(0.63, linestyle='--',color='black',label='Nonhuman Average')
    plt.legend(); 
    plt.title("Effect of Matched Availability on Number of Questions"); 
    plt.ylim([.5,1])


    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/avail_quests.png'); 


def humanVignetteExtract():
    allDat = []; 

    print("Extracting data for human test"); 

    mults = ['Human_Long','NonHuman_Long']

    for po in mults:
        print("Plan: {}".format(po)); 
        allStates = []; 
        for i in range(0,250):
            #print(i); 
            data = np.load('../data/{}/{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            #if(data['Captured'] == True):
                #allStates.append(data['TotalTime']); 
            allStates.append(data['States']); 
            del data
        allDat.append(allStates); 
    np.save('../data/human_nonhuman_states.npy',allDat);

    


def humanVignetteCheck(show=False):
    
    plt.figure(); 
    data = np.load('../data/human_nonhuman_states.npy',allow_pickle=True)
    


    hum_cands = [221]; 
    non_cands = [50]; 

    for run in hum_cands:

        #import the background image
        img = mpimg.imread('../img/overhead_mini_fit.png')
        plt.imshow(img); 




        s = np.array(data[0][run]); 

        plt.scatter(s[:,0],1000-s[:,1],color='green',alpha=0.8,s=2); 


        U = []; 
        V = []; 
        for i in range(0,len(s)-1):
            # U.append(s[i,0] -s[i+1,0])
            # V.append(s[i,1] -s[i+1,1])
            U.append(s[i+1,0] -s[i,0])
            V.append(s[i+1,1] -s[i,1])


        plt.quiver(s[:,0][0:-1],1000-s[:,1][0:-1], U,V, color=[[0,i/len(s[:,0]),.5*(1-(i/len(s[:,0])))] for i in range(0,len(s[:,0]))],alpha=0.8,headwidth=5,headlength=5)


        U = []; 
        V = []; 
        for i in range(0,len(s)-1):
            # U.append(s[i,0] -s[i+1,0])
            # V.append(s[i,1] -s[i+1,1])
            U.append(s[i+1,2] -s[i,2])
            V.append(s[i+1,3] -s[i,3])

        plt.scatter(s[:,2],1000-s[:,3],color='red',s=2); 
        plt.quiver(s[:,2][0:-1],1000-s[:,3][0:-1], U,V, color=[[i/len(s[:,0]),0,0] for i in range(0,len(s[:,0]))],alpha=0.8,headwidth=5,headlength=5)

        plt.title("Run: {}".format(run)); 

        if(show):
            plt.show(); 
        else:
            plt.savefig('../figs/human_vignette.png'); 



    fig = plt.figure(); 
    ims = []; 
    s = np.array(data[0][221]); 
    for i in range(0,len(s)):
        img = mpimg.imread('../img/overhead_mini_fit.png')
        plt.imshow(img); 
        #plt.scatter(s[:,0],1000-s[:,1],color='green',alpha=0.8,s=2); 
        plt.axis('off'); 
        imgarr1 = plt.scatter(s[0:i,2],1000-s[0:i,3],color=[[j/i,0,0] for j in range(0,i)], animated=True)
        imgarr2 = plt.scatter(s[0:i,0],1000-s[0:i,1],color=[[0,j/i,.5*(1-(j/i))] for j in range(0,i)], animated=True)

        ims.append([imgarr1,imgarr2]); 
    
    ani = animation.ArtistAnimation(fig,ims,interval=50,blit=True,repeat_delay=1000); 
    if(show):
        plt.show();
    else:
        ani.save('../figs/human_pursuit.gif',writer='imagemagick')


    plt.figure()
    for run in non_cands:

        #import the background image
        img = mpimg.imread('../img/overhead_mini_fit.png')
        plt.imshow(img); 




        s = np.array(data[1][run]); 

        plt.scatter(s[:,0],1000-s[:,1],color='green',alpha=0.8,s=2); 


        U = []; 
        V = []; 
        for i in range(0,len(s)-1):
            # U.append(s[i,0] -s[i+1,0])
            # V.append(s[i,1] -s[i+1,1])
            U.append(s[i+1,0] -s[i,0])
            V.append(s[i+1,1] -s[i,1])


        plt.quiver(s[:,0][0:-1],1000-s[:,1][0:-1], U,V, color=[[0,i/len(s[:,0]),.5*(1-(i/len(s[:,0])))] for i in range(0,len(s[:,0]))],alpha=0.8,headwidth=5,headlength=5)


        U = []; 
        V = []; 
        for i in range(0,len(s)-1):
            # U.append(s[i,0] -s[i+1,0])
            # V.append(s[i,1] -s[i+1,1])
            U.append(s[i+1,2] -s[i,2])
            V.append(s[i+1,3] -s[i,3])

        plt.scatter(s[:,2],1000-s[:,3],color='red',s=2); 
        plt.quiver(s[:,2][0:-1],1000-s[:,3][0:-1], U,V, color=[[i/len(s[:,0]),0,0] for i in range(0,len(s[:,0]))],alpha=0.8,headwidth=5,headlength=5)

        plt.title("Run: {}".format(run)); 

        if(show):
            plt.show(); 
        else:
            plt.savefig('../figs/Nonhuman_vignette.png'); 




    fig = plt.figure(); 
    ims = []; 
    s = np.array(data[1][50]); 
    for i in range(0,len(s)):
        img = mpimg.imread('../img/overhead_mini_fit.png')
        plt.imshow(img); 
        #plt.scatter(s[:,0],1000-s[:,1],color='green',alpha=0.8,s=2); 
        plt.axis('off'); 
        imgarr1 = plt.scatter(s[0:i,2],1000-s[0:i,3],color=[[j/i,0,0] for j in range(0,i)], animated=True)
        imgarr2 = plt.scatter(s[0:i,0],1000-s[0:i,1],color=[[0,j/i,.5*(1-(j/i))] for j in range(0,i)], animated=True)
        ims.append([imgarr1,imgarr2]); 
    
    ani = animation.ArtistAnimation(fig,ims,interval=50,blit=True,repeat_delay=1000); 
    if(show):
        plt.show();
    else:
        ani.save('../figs/nonhuman_patrol.gif',writer='imagemagick')



def sketchVignetteExtract():
    allDat = {'15s':[],'30s':[],'60s':[],'120s':[]}; 

    mults = ['15s','30s','60s','120s']

    for po in mults:
        print("Sketch Rate: {}".format(po)); 
        allSketches = []; 
        for i in range(0,100):
            #print(i); 
            data = np.load('../data/sketchRate_{}/sketchRate_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
            allDat[po].append(data['Sketches']); 


            del data
        
    np.save('../data/sketchRate_sketches.npy',allDat); 


def sketchVignetteCheck(show=False):
    
    data = np.load('../data/sketchRate_sketches.npy',allow_pickle=True).item(); 

    keySet = ['15s','30s','60s','120s']


    for key in keySet:
        allLengths = []
        for k in data[key]:
            allLengths.append(len(k)); 
        print("Key: {}, Mean Length: {}".format(key,np.mean(allLengths))); 

    #print(data['30s'][1][0].points)

    #for run in range(11,len(data['30s'])):

        # if(len(data['30s'][run]) < 12):
        #     continue; 

    plt.figure(); 
    img = mpimg.imread('../img/overhead_mini_fit.png')
    plt.imshow(img); 
    for r in data['30s'][11]: 
        plt.scatter(r.points[:, 0], 1000-r.points[:, 1],color='red',alpha=0.8, s=20);
        plt.plot([r.points[-1,0],r.points[0,0]], [1000-r.points[-1,1],1000-r.points[0,1]],color='black',linestyle='-', linewidth=2)
        for i in range(0,len(r.points)-1):
            plt.plot([r.points[i,0],r.points[i+1][0]],[1000-r.points[i,1],1000-r.points[i+1,1]],color='black',linestyle='-', linewidth=2)
    plt.title("~{} Questions".format((1+10*len(data['30s'][11]))));  
    plt.axis("Off")
    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/sketch_30.png'); 




    plt.figure(); 
    cand = 47; 
    img = mpimg.imread('../img/overhead_mini_fit.png')
    plt.imshow(img); 
    for r in data['60s'][cand]: 
        plt.scatter(r.points[:, 0], 1000-r.points[:, 1],color='red',alpha=0.8, s=20);
        plt.plot([r.points[-1,0],r.points[0,0]], [1000-r.points[-1,1],1000-r.points[0,1]],color='black',linestyle='-', linewidth=2)
        for i in range(0,len(r.points)-1):
            plt.plot([r.points[i,0],r.points[i+1][0]],[1000-r.points[i,1],1000-r.points[i+1,1]],color='black',linestyle='-', linewidth=2)
    plt.title("~{} Questions".format((1+10*len(data['60s'][cand])))); 
    #plt.xlabel(cand) 
    plt.axis("Off")
    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/sketch_60.png'); 


    plt.figure(); 
    cand = 23; 

    img = mpimg.imread('../img/overhead_mini_fit.png')
    plt.imshow(img); 
    for r in data['120s'][cand]: 
        plt.scatter(r.points[:, 0], 1000-r.points[:, 1],color='red',alpha=0.8, s=20);
        plt.plot([r.points[-1,0],r.points[0,0]], [1000-r.points[-1,1],1000-r.points[0,1]],color='black',linestyle='-', linewidth=2)
        for i in range(0,len(r.points)-1):
            plt.plot([r.points[i,0],r.points[i+1][0]],[1000-r.points[i,1],1000-r.points[i+1,1]],color='black',linestyle='-', linewidth=2)
    plt.title("~{} Questions".format((1+10*len(data['120s'][cand])))); 
    #plt.xlabel(cand) 
    plt.axis("Off")
    if(show):
        plt.show(); 
    else:
        plt.savefig('../figs/sketch_120.png'); 
 

if __name__ == '__main__':
    # #poisExtract(); 
    # poisCheck();
    # #amultExtract(); 
    # amultCheck(); 

    # #sketchRateExtract(); 
    # sketchRateCheck();

    # #accuracyDataExtract();  
    # accuracyDataCheck();

    # #availabilityDataExtract(); 
    # availabilityDataCheck(); 

    # #predictiveObsPlanningExtract(); 
    # predictiveObsPlanningCheck(); 

    #humanDataExtract(); 
    #humanDataCheck(False); 

    #predictiveStateObsExtract(); 
    #predictiveSlipAways(True); 

    #accQuestionsExtract(); 
    #accQuestionsCheck(False)

    #availQuestionsExtract(); 
    #availQuestionsCheck(False); 

    #humanVignetteExtract(); 
    #humanVignetteCheck(False); 

    #sketchVignetteExtract(); 
    sketchVignetteCheck(False); 
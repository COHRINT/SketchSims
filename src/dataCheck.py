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

    #allDat = []; 

    #for po in range(0,6):
        #print("Pois_Mean: {}".format(po)); 
        #allCatchTimes = []; 
        # for i in range(0,100):
        #     #print(i); 
        #     data = np.load('../data/Pois_{}/Pois_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
        #     if(data['Captured'] == True):
        #         allCatchTimes.append(data['TotalTime']); 
        #     del data
        # print('Average Catch Time: {}'.format(np.mean(allCatchTimes)));
        # print("Capture Standard Dev: {}".format(np.std(allCatchTimes)));  
        # print('Catch Rate: {}'.format(len(allCatchTimes)/100)); 
        # print(""); 
        #allDat.append(allCatchTimes); 

    #f,p = stats.f_oneway(allDat[0],allDat[1],allDat[2],allDat[3],allDat[4],allDat[5])

    #print("F-Statistic: {}".format(f)); 
    #print("P-value: {}".format(p)); 



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
    plt.scatter(x,allRatio,s=50,marker='*',color='black'); 
    plt.ylabel('Catch Ratio'); 
    plt.xlabel('Poisson Mean'); 
    plt.title("Effect of Varying Poisson Means on POMDP Performance"); 
    

    plt.figure(); 
    allTests = np.zeros(shape=(6,6)); 
    for i in range(0,6):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
        for j in range(i,6):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4,5,6],[3,4,5,6,7,8]); 
    plt.xticks([0,1,2,3,4,5,6],[3,4,5,6,7,8]); 
    plt.colorbar(); 
    plt.axis('tight'); 
    plt.title("Binomial Significance of Poisson Means"); 
    plt.show(); 


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

    # allDat = []; 

    # mults = ['1p5','2','3','4','5','10']

    # for po in mults:
    #     print("Area Multiplier: {}".format(po)); 
    #     allCatchTimes = []; 
    #     for i in range(0,100):
    #         #print(i); 
    #         data = np.load('../data/amult_{}/amult_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
    #         if(data['Captured'] == True):
    #             allCatchTimes.append(data['TotalTime']); 
    #         del data
    #     print('Average Catch Time: {}'.format(np.mean(allCatchTimes)));
    #     print("Capture Standard Dev: {}".format(np.std(allCatchTimes)));  
    #     print('Catch Rate: {}'.format(len(allCatchTimes)/100)); 
    #     print(""); 
    #     allDat.append(allCatchTimes); 

    # f,p = stats.f_oneway(allDat[0],allDat[1],allDat[2],allDat[3],allDat[4],allDat[5])

    # print("F-Statistic: {}".format(f)); 
    # print("P-value: {}".format(p)); 

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
    plt.scatter(x,allRatio,s=50,marker='*',color='black'); 
    plt.ylabel('Catch Ratio'); 
    plt.xlabel('Area Mutliplier'); 
    plt.title("Effect of Varying Near Area Multiplier on POMDP Performance"); 
    

    plt.figure(); 
    allTests = np.zeros(shape=(6,6)); 
    for i in range(0,6):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
        for j in range(i,6):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4,5,6],[1.5,2,3,4,5,10]); 
    plt.xticks([0,1,2,3,4,5,6],[1.5,2,3,4,5,10]); 
    plt.colorbar(); 
    plt.axis('tight'); 
    plt.title("Binomial Significance of Near Area Multipliers"); 
    plt.show(); 


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

    # allDat = []; 

    # #mults = ['15s','30s','60s','90s','120s']
    # #mults = ['15s','30s','60s','90s','120s','150s']
    # mults = ['15s','30s','60s','120s','240s','inf']

    # for po in mults:
    #     print("Human Sketch Rate: {}".format(po)); 
    #     allCatchTimes = []; 
    #     for i in range(0,100):
    #         #print(i); 
    #         data = np.load('../data/sketchRate_{}/sketchRate_{}_{}.npy'.format(po,po,i), allow_pickle=True).item(); 
    #         # suma = 0; 
    #         # for j in data['Sketches']:
    #         #     if(j is not None):
    #         #         suma += 1; 
    #         # print(suma); 
    #         if(data['Captured'] == True):
    #             allCatchTimes.append(data['TotalTime']); 
    #         del data
    #     print('Average Catch Time: {}'.format(np.mean(allCatchTimes)));
    #     print("Capture Standard Dev: {}".format(np.std(allCatchTimes)));  
    #     print('Catch Rate: {}'.format(len(allCatchTimes)/100)); 
    #     print(""); 
    #     allDat.append(allCatchTimes); 

    # f,p = stats.f_oneway(allDat[0],allDat[1],allDat[2],allDat[3],allDat[4],allDat[5])

    # print("F-Statistic: {}".format(f)); 
    # print("P-value: {}".format(p)); 

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
    plt.scatter(x,allRatio,s=50,marker='*',color='black'); 
    plt.xticks([15,30,60,120,240],[15,30,60,120,'inf']); 
    plt.ylabel('Catch Ratio'); 
    plt.xlabel('Sketch Rate (s)'); 
    plt.title("Effect of Varying Sketch Rate on POMDP Performance"); 
    

    plt.figure(); 
    allTests = np.zeros(shape=(5,5)); 
    for i in range(0,5):
        for j in range(0,i):
            allTests[i,j] = stats.binom_test(allRatio[i]*100,n=100,p=allRatio[j]); 
        for j in range(i,5):
            allTests[i,j] = np.nan; 

        allTests[i,i] = np.nan; 
    plt.imshow(allTests,vmax=1.0,vmin=0);
    plt.yticks([0,1,2,3,4],[15,30,60,120,'inf']); 
    plt.xticks([0,1,2,3,4],[15,30,60,120,'inf']); 
    plt.colorbar(); 
    plt.axis('tight'); 
    plt.title("Binomial Significance of Sketch Rate"); 
    plt.show(); 


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
            #x.append(int(ac)); 
            #y.append(int(ac2)); 
            #colors.append([1-data[ac][ac2],data[ac][ac2],0]); 
        x.append(tmp); 
    fig,axarr = plt.subplots(2,2); 

    axarr[0][0].imshow(x,origin='lower left'); 
    axarr[0][0].set_ylabel("Actual"); 
    axarr[0][0].set_xlabel("Assumed"); 
    axarr[0][0].set_xticks([0,1,2,3,4]); 
    axarr[0][0].set_yticks([0,1,2,3,4]); 
    axarr[0][0].set_xticklabels([.3,.5,.7,.9,.95]); 
    axarr[0][0].set_yticklabels([.3,.5,.7,.9,.95]); 

   


    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[i][j]/5; 
        tmp.append(suma); 
    axarr[0][1].plot(tmp,rangX); 
    axarr[0][1].set_ylabel('Actual Accuracy'); 
    axarr[0][1].set_xlabel("Catch Rate"); 
    # tmp = np.array([tmp,tmp]).T
    # axarr[0][1].contourf(tmp); 
    # axarr[0][1].set_axis_off(); 

    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[j][i]/5; 
        tmp.append(suma); 
    axarr[1][0].plot(rangX,tmp); 
    axarr[1][0].set_ylabel("Catch Rate"); 
    axarr[1][0].set_xlabel("Assumed Accuracy"); 
    # tmp = np.array([tmp,tmp])
    # axarr[1][0].contourf(tmp); 
    # axarr[1][0].set_axis_off(); 


    tmp = []; 
    for i in range(0,5):
        tmp.append(x[i][i]); 
    axarr[1][1].plot(rangX,tmp); 
    axarr[1][1].set_xlabel("Matched Accuracy"); 
    axarr[1][1].set_ylabel("Catch Rate"); 
    #axarr[1][1].set_axis_off(); 


    plt.tight_layout()

    #axarr[0][0].colorbar();  
    plt.show();


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
            #x.append(int(ac)); 
            #y.append(int(ac2)); 
            #colors.append([1-data[ac][ac2],data[ac][ac2],0]); 
        x.append(tmp); 
    fig,axarr = plt.subplots(2,2); 

    axarr[0][0].imshow(x,origin='lower left'); 
    axarr[0][0].set_ylabel("Actual"); 
    axarr[0][0].set_xlabel("Assumed"); 
    axarr[0][0].set_xticks([0,1,2,3,4]); 
    axarr[0][0].set_yticks([0,1,2,3,4]); 
    axarr[0][0].set_xticklabels([.3,.5,.7,.9,.95]); 
    axarr[0][0].set_yticklabels([.3,.5,.7,.9,.95]); 

   


    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[i][j]/5; 
        tmp.append(suma); 
    axarr[0][1].plot(tmp,rangX); 
    axarr[0][1].set_ylabel('Actual Availability'); 
    axarr[0][1].set_xlabel("Catch Rate"); 
    # tmp = np.array([tmp,tmp]).T
    # axarr[0][1].contourf(tmp); 
    # axarr[0][1].set_axis_off(); 

    tmp = [];
    rangX = [.3,.5,.7,.9,.95];  
    for i in range(0,5):
        suma = 0; 
        for j in range(0,5):
            suma += x[j][i]/5; 
        tmp.append(suma); 
    axarr[1][0].plot(rangX,tmp); 
    axarr[1][0].set_ylabel("Catch Rate"); 
    axarr[1][0].set_xlabel("Assumed Availability"); 
    # tmp = np.array([tmp,tmp])
    # axarr[1][0].contourf(tmp); 
    # axarr[1][0].set_axis_off(); 


    tmp = []; 
    for i in range(0,5):
        tmp.append(x[i][i]); 
    axarr[1][1].plot(rangX,tmp); 
    axarr[1][1].set_xlabel("Matched Availability"); 
    axarr[1][1].set_ylabel("Catch Rate"); 
    #axarr[1][1].set_axis_off(); 


    plt.tight_layout()

    #axarr[0][0].colorbar();  
    plt.show();


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
    plt.bar([0,1],allRatio); 
    plt.ylabel('Catch Ratio'); 
    #plt.xlabel('Sketch Rate (s)'); 
    plt.xticks([0,1],['Blind','Predictive']); 
    plt.title("Effect of Predictive Tree Planning on POMDP Performance"); 
    


    test = stats.binom_test(allRatio[1]*100,n=100,p=allRatio[0]); 

    print("Binomial Significance of Predictive Planning: {}".format(test)); 
    plt.show();

if __name__ == '__main__':
    #poisExtract(); 
    #poisCheck();
    #amultExtract(); 
    #amultCheck(); 

    #sketchRateExtract(); 
    #sketchRateCheck();

    #accuracyDataExtract();  
    #accuracyDataCheck();

    #availabilityDataExtract(); 
    #availabilityDataCheck(); 

    #predictiveObsPlanningExtract(); 
    predictiveObsPlanningCheck(); 

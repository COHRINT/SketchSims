import numpy as np; 


#a = np.load('../data/simHARPS_Test.npy').item(); 

#print(a['tag'])

def check():

    hum = np.load("../../../../../mnt/d/SimHARPS/simHARPS_Human_nom.npy").item(); 
    #hum = np.load("../../../../../mnt/d/SimHARPS/simHARPS_Nonhuman_nom.npy").item(); 

    allTimes = []; 
    allCatchTimes = []; 

    for sim in hum['sims']:
        allTimes.append(sim['TotalTime']); 
        if(sim['TotalTime'] < 300):
            allCatchTimes.append(sim['TotalTime']); 

    print("Average Time: {}".format(np.mean(allTimes)))
    print("Average Catch Time: {}".format(np.mean(allCatchTimes))); 
    print("Ratio of Capture: {}".format(len(allCatchTimes)/len(allTimes)));

if __name__ == '__main__':
    check(); 


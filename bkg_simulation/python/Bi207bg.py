#/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from random import random as rndm 
from pathlib import Path

import inc.GV

start_time = time.time()

if __name__ == "__main__":
    
    if len(sys.argv) == 2: 
        N = int(sys.argv[1])
    else:
        N = 1E6
        
    inc.GV.globalVariables()
    
    sctmax=0.
    ivect = [0] * 10 # counts the number of interactions per wire
    pi2=2.*math.pi
    
    #Preparing histos
    h1d_x0 = []
    h1d_y0 = []
    
    # Initializing output files
    Path("./Output").mkdir(parents=True, exist_ok=True)
    outfile_allParticles = open("./Output/allParticles.csv", "w")
    outfile_allParticles.write("i,d,x1,y1,z1,i1,Energy,ComptE,rr")
    files = [open(f"./Output/chn_r{i:02d}.csv", "w") for i in range(1, 9)]
    headers = "iele,ComptE,rr\n"
    
    for file in files:
        file.write(headers)

    i=0
    while i<N:
        
        # if i%(N/100) == 0:
        #     print(f'{i:.2E} particles simulated out of {N:.2E} in {round((time.time() - start_time),4)} s')
        
        # Normalization to prb9; rndm() only returns values between 0 and 1
        Aprob = inc.GV.prb[9]*rndm() 
    	    
        # Determination of the generated particle (0=photons, 1=electrons)
        # Electrons interact at distance = 0
        # --------------------------------------------------------------------
        data = [(Aprob < inc.GV.prb[1], (inc.GV.GamInt[1], inc.GV.GamEne[1], 0)),
            (Aprob < inc.GV.prb[2], (inc.GV.GamInt[2], inc.GV.GamEne[2], 0)),
            (Aprob < inc.GV.prb[3], (inc.GV.GamInt[3], inc.GV.GamEne[3], 0)),
            (Aprob < inc.GV.prb[4], (0., inc.GV.EleEne[1], 1)),
            (Aprob < inc.GV.prb[5], (0., inc.GV.EleEne[2], 1)),
            (Aprob < inc.GV.prb[6], (0., inc.GV.EleEne[3], 1)),
            (Aprob < inc.GV.prb[7], (0., inc.GV.EleEne[4], 1)),
            (Aprob < inc.GV.prb[8], (0., inc.GV.EleEne[5], 1)),
            (True, (0., inc.GV.EleEne[6], 1))]
        for condition, values in data:
            if condition:
                DInter, Energy, iele = values
                break
        # --------------------------------------------------------------------
            
        # Generation of the event position on the surface of the source 
        
        xc=0.
        yc=0.
        r=5 #mm
        
        x0=(-1)**round(10*rndm(),0)*r*rndm()
        y0=(-1)**round(10*rndm(),0)*r*rndm()
        
        # Condition for a circle
        if (x0-xc)**2+(y0-yc)**2 < r**2 :
            
            i=i+1

            z0=0.
            
            h1d_x0.append(x0)
            h1d_y0.append(y0)
            
            # interaction distance
            
            # P (gamma travels a distance X w/o interacting) = exp(-X/lambda) 
            # lambda = interaction length, P ranges in 0-1
            # Extract a value P in 0-1 to simulate an interaction distance X, 
            # then invert the P expression to get X = - lambda * log(P)   
            
            d=-DInter*np.log(rndm())
            
            # direction of the next step
            phi=rndm()*pi2 #rad
            ctheta=rndm()
            stheta=np.sqrt(1.-ctheta*ctheta)
            
            # point where the gamma interacted
            x1=x0+d*stheta*np.sin(phi)
            y1=y0+d*stheta*np.cos(phi)
            z1=z0+d*ctheta
            r1=np.sqrt(x1*x1+y1*y1)
            
            # cuts
            i1=9999
            if(z1>=0. and z1<inc.GV.height) :
                
                # selection of wires 
                # checking if the point is within the set of wires or not
                
                y1p=+x1*inc.GV.pitch+inc.GV.edge
                y1m=+x1*inc.GV.pitch-inc.GV.edge
                y2p=-x1*inc.GV.pitch+inc.GV.edge
                y2m=-x1*inc.GV.pitch-inc.GV.edge
                
                # condition for the generated particle to be inside 
                # the exagonal tower given by Induction strip 1 and 2 xmin,xmax, ymin,ymax
                
                if(y1>y1m and y1<y1p and y1>y2m and y1<y2p and x1>-20 and x1<+20) :
                    
                    i1=int((x1+20.)/5.+1) #casting to int here
                    # print(i1)
                      
                    # if electron flag = 0 i.e. if it's a photon
                    if(iele==0) :
                        iflg=0
                        gg=Energy/0.511
                        while(iflg==0):
                            ct=2.*rndm()-1.
                            eps=1./(1.+gg*(1.-ct))
                            sctprob=0.5*eps**2*(eps+1./eps-(1.-ct**2))
    
                            if(rndm()<=sctprob) :
                               iflg=1
                               ComptE=Energy*(1.-1./(1.+gg*(1-ct)))
                    # electron    
                    else:
                        ComptE=Energy 
                        
                        # Introducing some noise to account for resolution
                        # if(rndm()<=0.33): 
                        # ComptE=ComptE*rndm()
                          
                    # For the 1 MeV (1063 keV) only. 
                    # Other decays have different resolutions. 
                    # We could add a square root factor of the energy   
                    res=0.   
                    # Generation of a random number from a gaussian distribution
                    for k in np.arange(1,13,1):
                       res=res+rndm()
                          
                    res=inc.GV.photonRes*(res-6.) # Why -6? # from data (? - check!!!)
                    rr=ComptE+res # Final energy
                        
                    line = f"{i},{round(d,3)},{round(x1,3)},{round(y1,3)},{round(z1,3)},{round(i1,3)},{round(Energy,6)},{round(ComptE,6)},{round(rr,6)}"
                    
                    outfile_allParticles.write("\n"+line)
                            
                    # Gaussian distributed threshold
                    rth=0.                 
                    for k in np.arange(1,13,1):
                       rth=rth+rndm()
                          
                    rth=0.09*(rth-6.) #normalization to a threshold of 90 keV
                    
                    
                    if(ComptE>=(.32+rth)) :
                        files[i1-1].write(f"{iele},{ComptE},{rr}\n")
    
                    if(i1>0 and i1<9):
                        ivect[i1]=ivect[i1]+1
  
    print (ivect) # counts the number of interactions per wire
    
    outfile_allParticles.close()
    
    for file in files:
        file.close()
        
    # Plotting start histogram
    plt.hist2d(h1d_x0,h1d_y0, bins=40, cmap=plt.cm.jet)
    
    cb = plt.colorbar()
    cb.set_label('Counts')
    
    plt.xlabel('x [mm]')
    plt.ylabel('y [mm]')
    plt.title('Emission position')
    
    # Set the limits of the plot
    plot_frame = 1.0
    plt.xlim(-1*plot_frame*r, plot_frame*r)
    plt.ylim(-1*plot_frame*r, plot_frame*r)
    
    # Set the ticks and labels on the x axis
    x_ticks = np.linspace(-plot_frame*r, plot_frame*r, 11)
    x_ticklabels = ['{:0.0f}'.format(x) for x in x_ticks]
    plt.xticks(x_ticks, x_ticklabels)
    
    # Set the ticks and labels on the y axis
    y_ticks = np.linspace(-plot_frame*r, plot_frame*r, 11)
    y_ticklabels = ['{:0.0f}'.format(y) for y in y_ticks]
    plt.yticks(y_ticks, y_ticklabels)
    
    # set grid
    plt.grid(color='grey', linestyle='-', linewidth=0.5)
    
    # save and show plot
    plt.savefig("./Output/h2d_EmissionXY.pdf")
    plt.show()

print("\n--- Execution time: %s s ---" % round((time.time() - start_time),4))

        
        
        
        
        
        
        
        
        
        
        
        






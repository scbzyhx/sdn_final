#!/usr/bin/python

import matplotlib.pyplot as plt

#plt.figure(1)
if __name__ == "__main__":
    yy = []
    with open('speed.txt','r') as f:
        for line in f:
            
            if line != '':
                print line
                yy.append(int(line))
        plt.ylabel('speed (B/s)')
        plt.xlabel('time')
        plt.plot(yy)
        plt.show()

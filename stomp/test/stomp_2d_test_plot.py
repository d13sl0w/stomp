#!/usr/bin/env python

import matplotlib
matplotlib.use('GtkAgg')
import matplotlib.pyplot as plt
import numpy
import time
import os

# ugly function required for old version of matplotlib
def pause(plt, interval):
    figManager = plt._pylab_helpers.Gcf.get_active()
    if figManager is not None:
        canvas = figManager.canvas
        canvas.draw()
        was_interactive = plt.isinteractive()
        if not was_interactive:
            plt.ion()
            plt.show(False)
        canvas.start_event_loop(interval)
        if not was_interactive:
            plt.ioff()
        return

class Stomp2DTestPlotter:
    def __init__(self, directory):
        self.directory = directory
        self.lines_plotted = False

    def load_cost_function(self):
        f = open(self.directory+'/cost_function.txt')
        dims = [int(x) for x in f.readline().strip().split('\t')]
        X = numpy.zeros((dims[0], dims[1]))
        Y = numpy.zeros((dims[0], dims[1]))
        C = numpy.zeros((dims[0], dims[1]))
        x = int(0)
        y = int(0)
        for line in f:
            entries = [float(i) for i in line.strip().split('\t')]
            X[x,y] = entries[0]
            Y[x,y] = entries[1]
            C[x,y] = entries[2]
            y += 1
            if y >= dims[1]:
                y = 0
                x += 1
        f.close()
        self.X = X;
        self.Y = Y;
        self.C = C;

    def plot_cost_function(self):
        im = plt.imshow(self.C.transpose(), extent=(0,1,0,1), origin='lower', cmap=plt.cm.jet)
        im.set_interpolation('bilinear')
        #plt.pcolor(self.X,self.Y,self.C)

    def animate_trajectories(self, save_figures):
        num_rollouts_data = numpy.genfromtxt(self.directory+'/num_rollouts.txt')
        cost_data = numpy.genfromtxt(self.directory+'/costs.txt')
        stddev_data = numpy.genfromtxt(self.directory+'/stddevs.txt')
        num_iterations = num_rollouts_data.size
        for i in range(0,num_iterations):
            if self.lines_plotted:
                self.noiseless_line[0].remove()
                for line in self.noisy_lines:
                    line[0].remove()

            file_name = self.directory+'/noiseless_%d.txt'%(i)
            data = numpy.genfromtxt(file_name)
            self.noiseless_line = plt.plot(data[:,0], data[:,1], 'g*-', aa=True, linewidth=3)
            self.noisy_lines = []

            if i>0:
                num_rollouts = int(num_rollouts_data[i-1])
                for j in range(0,num_rollouts):
                    file_name = self.directory+'/noisy_%d_%d.txt'%(i,j)
                    if not os.path.exists(file_name):
                      continue
                    data2 = numpy.genfromtxt(file_name)
                    self.noisy_lines.append(plt.plot(data2[:,0], data2[:,1], 'r', linewidth=0.5, aa=True))
                cost = cost_data[i-1]
                stddevs = stddev_data[i-1,:]
                print "%3d)\tCost=%f\tNoise=[%f, %f]"%(i,cost,stddevs[0],stddevs[1])
            
            #line.set_xdata(data[:,0]);
            #line.set_ydata(data[:,1]);
            #plt.draw()
            pause(plt, 0.000001)
            #raw_input()
            self.lines_plotted = True
            if save_figures:
                file_name = self.directory+'/%d.png'%(i)
                print file_name
                plt.savefig(file_name, dpi=300, bbox_inches='tight', pad_inches=0.01)
            
        plt.show()

if __name__=='__main__':
    plt.figure(1)
    plt.draw()
    s = Stomp2DTestPlotter('.')
    s.load_cost_function()
    s.plot_cost_function()
    plt.axis([0,1,0,1])
    s.animate_trajectories(False)

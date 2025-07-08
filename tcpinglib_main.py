from tcppinglib import tcpping
import time
import multiprocessing as mp

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp

def plot_subproc(y_q: mp.Queue):
    plt.close()

    y_data=[]



    #Update routine that is called by FuncAnimation instance to update plot data, returns 2D tuple that is used to graph
    def update(frame,y_q: mp.Queue):
        nonlocal y_data

        #check if queue is not empty before getting from queue
        # print("Queue",y_q.qsize())

        if y_q.empty() == False:

            ax2.clear()
            ax2.plot(range(0,len(y_data)),y_data)
            ax2.grid(alpha=0.7)
            
            y_data_20 =[]
            if len(y_data)>20:
                y_data_20 = y_data[len(y_data)-21:]

            while y_q.qsize() >0:
                y_data.append(y_q.get())
            ax.clear()
            ax.grid(alpha=0.7)
            ax.boxplot(y_data,vert=False,widths=0.7)
            ax.scatter( y_data,[1]*len(y_data), alpha=0.6, color='blue', label='Data Points')
            figure.gca().relim()
            figure.gca().autoscale_view()
            

            

            ax3.clear()
            ax3.grid(alpha=0.7)
            ax3.boxplot(y_data_20,vert=False,widths=0.7)
            ax3.scatter( y_data_20,[1]*len(y_data_20), alpha=0.6, color='blue', label='Data Points')

    
            if ax.get_xlim()[1]>ax3.get_xlim()[1]:
                ax3.set_xlim(ax.get_xlim())
            else:
                ax.set_xlim(ax3.get_xlim())

        # line.set_data(x_data,y_data)
        # figure.gca().relim()
        # figure.gca().autoscale_view()
        # return line,

        


    #while loop for reopening plot window
    while True:
        #Initialize plot
        figure = plt.figure(num=1,figsize=(7,4))
        ax = figure.add_subplot(3,1,1)
        ax.clear()
        ax.set_title("Ping test")
        ax.set_xlabel("Ping")
        ax.grid(alpha=0.7)
        ax.boxplot(y_data)

        ax2 = figure.add_subplot(3,1,3)
        ax2.plot(y_data,range(0,len(y_data)))

        ax3 = figure.add_subplot(3,1,2)

        animation = FuncAnimation(figure, update,fargs=[y_q], interval=1000,cache_frame_data=False)
        plt.show()
        time.sleep(0.5)



def main():
    
    data_q = mp.Queue()
    plot_window = mp.Process(target=plot_subproc,args=[data_q])
    plot_window.start()

    while True:
        host = tcpping("10.145.27.124",53,1,1)
        print(host.min_rtt)
        if host.min_rtt != 0:
            data_q.put(host.min_rtt)
        time.sleep(0.25)


if __name__ == '__main__':
    mp.freeze_support()
    main()
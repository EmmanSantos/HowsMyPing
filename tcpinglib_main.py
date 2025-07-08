# from tcppinglib import tcpping
from icmplib import ping
import time
import multiprocessing as mp
import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp

def plot_subproc(y_q: mp.Queue):
    plt.close()

    y_data=[]
    y_data_len1 =[]
    new_data_count = 0
    len_1 = 20
    len_2 = 100
    y_data_len = 0
    loss_arr = []
    loss_arr_len = 0


    #Update routine that is called by FuncAnimation instance to update plot data, returns 2D tuple that is used to graph
    def update(frame,y_q: mp.Queue):
        nonlocal y_data
        nonlocal y_data_len1
        nonlocal new_data_count
        nonlocal len_1
        nonlocal len_2
        nonlocal y_data_len
        nonlocal loss_arr
        nonlocal loss_arr_len
        


        if y_q.empty() == False:

            # get all in queue
            while y_q.qsize() >0:
                last_q = y_q.get()
                
                if last_q !=0:
                    y_data.append(last_q)
                    loss_arr.append(0)
                    loss_arr_len +=1
                
                    if y_data_len < 100:
                        y_data_len+=1

                    new_data_count +=1
                else:
                    loss_arr.append(1)
                    loss_arr_len +=1
            
            if loss_arr_len >100:
                loss_arr_len = 100

            y_data_len1 = y_data[-len_1:] if y_data_len>=len_1 else y_data
            y_data = y_data[-len_2:] if y_data_len>=len_2 else y_data
            loss_arr = loss_arr[-len_2:] if loss_arr_len>=len_2 else loss_arr
   
        
            ax2.clear()
            ax2.set_title("Packet Loss: "+str(sum(loss_arr))+"/"+str(loss_arr_len))
            ax2.plot(range(0,y_data_len),y_data)
            ax2.grid(alpha=0.7)
            
            if new_data_count>= 5:

                

                ax.clear()
                ax.grid(alpha=0.7)
                ax.boxplot(y_data,vert=False,widths=0.7)
                ax.scatter( y_data,[1]*y_data_len, alpha=0.6, color='blue', label='Data Points')
                

                

                ax3.clear()
                ax3.grid(alpha=0.7)
                ax3.boxplot(y_data_len1,vert=False,widths=0.7)
                ax3.scatter( y_data_len1,[1]*len(y_data_len1), alpha=0.6, color='blue', label='Data Points')

        
                if ax.get_xlim()[1]>ax3.get_xlim()[1]:
                    ax3.set_xlim(ax.get_xlim())
                else:
                    ax.set_xlim(ax3.get_xlim())
                new_data_count = 0

        # line.set_data(x_data,y_data)
        # figure.gca().relim()
        # figure.gca().autoscale_view()
        # return line,

        


    #while loop for reopening plot window
    while True:
        #Initialize plot
        figure = plt.figure(num=1,figsize=(7,4))
        ax = figure.add_subplot(3,1,2)
        ax.clear()
        ax.set_title("Ping test")
        ax.set_xlabel("Ping")
        ax.grid(alpha=0.7)
        ax.boxplot(y_data)

        ax2 = figure.add_subplot(3,1,1)
        ax2.plot(y_data,range(0,len(y_data)))

        ax3 = figure.add_subplot(3,1,3)

        animation = FuncAnimation(figure, update,fargs=[y_q], interval=500,cache_frame_data=False)
        plt.show()
        time.sleep(0.5)



def main():
    
    data_q = mp.Queue()
    loss_q = mp.Queue()
    plot_window = mp.Process(target=plot_subproc,args=[data_q])
    plot_window.start()
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = "8.8.8.8"

    while True:

        # host = tcpping("10.145.27.124",53,1,1)
        host = ping(ip,1,timeout=1)
        if host.packets_received != 0 and host.min_rtt == 0:
            data_q.put(0.0001)
            continue
        print(host.min_rtt)
        data_q.put(host.min_rtt)
        time.sleep(0.5)


if __name__ == '__main__':
    mp.freeze_support()
    main()
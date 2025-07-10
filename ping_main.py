import configparser
from icmplib import ping
import time
import multiprocessing as mp
import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp

def plot_subproc(y_q: mp.Queue,ip: str):
    plt.close()

    config = configparser.ConfigParser()
    config.read('./config.ini')

    y_data=[] # ping data without timeouts
    y_data_len = 0 # len is incremented manually to save CPU time
    y_data_len1 =[] # subset of ydata containing the last len1 samples
    new_data_count = 0 # count for updating box plots
    len_1 = int(config.get('DEFAULT','smaller_length',fallback=20))
    len_2 = int(config.get('DEFAULT','main_length',fallback=100))
    
    loss_arr = [] # counting dropped packets
    loss_arr_len = 0

    all_data = [] # contains all ping measurements including dropped packets
    all_data_len = 0

    #Update routine that is called by FuncAnimation instance to update plot data, returns 2D tuple that is used to graph
    def update(frame,y_q: mp.Queue):
        nonlocal ip

        nonlocal y_data
        nonlocal y_data_len1
        nonlocal new_data_count
        nonlocal len_1
        nonlocal len_2
        nonlocal y_data_len
        nonlocal loss_arr
        nonlocal loss_arr_len

        nonlocal all_data
        nonlocal all_data_len

        if y_q.empty() == False:

            # get all in queue
            while y_q.qsize() >0:
                last_q = y_q.get()
                
                # if positive packet is not dropped
                if last_q >=0:
                    y_data.append(last_q)

                    # append 0 to loss array  - means no packet lost
                    loss_arr.append(0)
                    loss_arr_len +=1

                    # length is stored because len() is slow
                    if y_data_len < len_2:
                        y_data_len+=1

                    new_data_count +=1
                else:
                    # append 1 to loss array  - means packet lost
                    loss_arr.append(1)
                    loss_arr_len +=1

                    # plot packet loss
                    
                
                all_data.append(last_q)
                all_data_len+=1

            # Caps the length of the  arrays
            if loss_arr_len >len_2:
                loss_arr_len = len_2

            if all_data_len >len_2:
                all_data_len = len_2

            # discards older data if longer than desired length
            y_data_len1 = y_data[-len_1:] if y_data_len>=len_1 else y_data
            y_data = y_data[-len_2:] if y_data_len>=len_2 else y_data
            loss_arr = loss_arr[-len_2:] if loss_arr_len>=len_2 else loss_arr

            all_data = all_data[-len_2:] if all_data_len>=len_2 else all_data
            
            
            # update time plot
            ax2.clear()
            ax2.set_title("Pinging: "+ip+" | Packet Loss: "+str(sum(loss_arr))+"/"+str(loss_arr_len)+" | Last Ping: "+str(last_q if last_q >=0 else "Timeout"))
            ax2.plot(range(0,all_data_len),all_data)
            ax2.grid(alpha=0.7)
            
            # plot timeouts
            for x, y in zip(range(0,all_data_len), all_data):
                if y < 0:
                    ax2.axvspan(x - 0.1, x + 0.1, color='red', alpha=0.3)

            # update boxplots if new packets received are over the threshold
            if new_data_count>= int(config.get('DEFAULT','boxplot_refresh_count',fallback=4)):
                
                # update boxplot 1
                ax.clear()
                ax.grid(alpha=0.7)
                ax.tick_params(labelbottom=False)
                box1 =ax.boxplot(y_data,vert=False,widths=0.7,tick_labels= ['Last '+str(y_data_len)])
                ax.scatter( y_data,[1]*y_data_len, alpha=0.6, color='blue', label='Data Points')
                
                # get boxplot 1 stats
                mean = round(sum(y_data)/y_data_len,2)
                median = box1['medians'][0]
                median =round(median.get_xdata()[0],2)
                stats = 'Mean: '+str(mean)+'\nMedian: '+str(median)
                ax.text(1.01,0.5,stats, ha = 'left',va = 'center',fontsize='small',transform = ax.transAxes )
                
                # draw mean
                ax.axvline(mean, color='purple', alpha=0.8)

                # update boxplot 2          
                ax3.clear()
                ax3.grid(alpha=0.7)
                box2 = ax3.boxplot(y_data_len1,vert=False,widths=0.7,tick_labels = ['Last '+str(y_data_len if y_data_len < len_1 else len_1 )])
                ax3.scatter( y_data_len1,[1]*len(y_data_len1), alpha=0.6, color='blue', label='Data Points')

                # get boxplot 2 stats
                mean2 = round(sum(y_data_len1)/(y_data_len if y_data_len < len_1 else len_1),2)
                median2 = box2['medians'][0]
                median2 = round(median2.get_xdata()[0],2)
                stats2 = 'Mean: '+str(mean2)+'\nMedian: '+str(median2)
                ax3.text(1.01,0.5,stats2, ha = 'left',va = 'center',fontsize='small',transform = ax3.transAxes)
                
                # draw mean
                ax3.axvline(mean2, color='purple', alpha=0.8)

        
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
        figure = plt.figure(num=1,figsize=(8,4),constrained_layout=True)

        # boxplot 1
        ax = figure.add_subplot(3,1,2)
        ax.clear()
        ax.grid(alpha=0.7)
        ax.boxplot(y_data)

        # timeplost
        ax2 = figure.add_subplot(3,1,1)
        ax2.plot(y_data,range(0,len(y_data)))

        # boxplot 2
        ax3 = figure.add_subplot(3,1,3)

        # plot is an animation running on a subprocess so pings continue and are not blocked by plot
        animation = FuncAnimation(figure, update,fargs=[y_q], interval=int(config.get('DEFAULT','fig_refresh',fallback=500)),cache_frame_data=False)
        plt.show()
        time.sleep(0.5)



def main():

    config = configparser.ConfigParser()
    config.read('./config.ini')
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = str(config.get('DEFAULT','ip',fallback='8.8.8.8'))

    data_q = mp.Queue()
    plot_window = mp.Process(target=plot_subproc,args=[data_q,ip])
    plot_window.start()

    while True:

        # host = tcpping("10.145.27.124",53,1,1)
        host = ping(ip,1,timeout=float(config.get('DEFAULT','timeout',fallback=1)))
        if host.packets_received ==0:
            data_q.put(-0.0001) #place negative number to indicate timeout; simplifies graphing the timeouts and reduces CPU usage
            print("Timeout")
        else:
            print(host.min_rtt)
            data_q.put(host.min_rtt)
            time.sleep(float(config.get('DEFAULT','interval',fallback=0.5)))


if __name__ == '__main__':
    try:
        mp.freeze_support()
        main()
    except Exception as e:
        print("Error: {}".format(e))
        input("Enter to Close")
        raise e
        
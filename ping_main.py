import configparser
from icmplib import ping
import time
import multiprocessing as mp
import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp

def is_close_tuple(t1, t2, tol=1e-2):
    return all(abs(a - b) <= tol for a, b in zip(t1, t2))

def draw_boxplot_stats(data: list, length: int,boxplot: plt.Axes,boxplot_dict: dict,config: configparser.ConfigParser):
    '''
    Generate stats list beside each box plot
    
    '''
    # get boxplot 1 stats
    stats_str =''
    if eval(config.get('DEFAULT','mean',fallback='True')):
        mean = round(sum(data)/length,2)
        stats_str += 'Mean: '+str(mean)
        # draw mean
        boxplot.axvline(mean, color='purple', alpha=0.8)

    if eval(config.get('DEFAULT','median',fallback='True')):
        if stats_str!= '': stats_str+='\n'
        median = boxplot_dict['medians'][0]
        median =round(median.get_xdata()[0],2)
        stats_str += 'Median: '+str(median)

    if eval(config.get('DEFAULT','maximum',fallback='True')):
        if stats_str!= '': stats_str+='\n'
        stats_str += 'Max: '+str(max(data))

    if eval(config.get('DEFAULT','minimum',fallback='True')):
        if stats_str!= '': stats_str+='\n'
        stats_str += 'Min: '+str(min(data))

    boxplot.text(1.01,0.5,stats_str, ha = 'left',va = 'center',fontsize='small',transform = boxplot.transAxes )
        
    return

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


    all_data = [] # contains all ping measurements including dropped packets
    all_data_len = 0
    x_all_data = []

    last_lims1 = ()
    last_lims2 = ()

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

        nonlocal all_data
        nonlocal all_data_len
        nonlocal x_all_data

        nonlocal ping_line

        nonlocal last_lims1
        nonlocal last_lims2

        if y_q.empty() == False:

            # get all in queue
            while y_q.qsize() >0:
                last_q = y_q.get()
                
                # if positive packet is not dropped
                if last_q >=0:
                    y_data.append(last_q)

                    # append 0 to loss array  - means no packet lost
                    loss_arr.append(0)


                    # length is stored because len() is slow
                    if y_data_len < len_2:
                        y_data_len+=1

                    new_data_count +=1
                else:
                    # append 1 to loss array  - means packet lost
                    loss_arr.append(1)


                    # plot packet loss

                
                all_data.append(last_q)
                all_data_len+=1
                if all_data_len<=len_2: x_all_data.append(all_data_len) 
                

                
                

            # Caps the length of the  arrays

            if all_data_len >len_2:
                all_data_len = len_2

            # discards older data if longer than desired length
            y_data_len1 = y_data[-len_1:] if y_data_len>=len_1 else y_data
            y_data = y_data[-len_2:] if y_data_len>=len_2 else y_data
            loss_arr = loss_arr[-len_2:] if all_data_len>=len_2 else loss_arr

            all_data = all_data[-len_2:] if all_data_len>=len_2 else all_data
            
            
            # update time plot
            for artist in timeplot.lines:
                artist.remove()
            for patch in timeplot.patches[:]:
                patch.remove()
            timeplot.set_prop_cycle(None) 
            timeplot.set_title("Pinging: "+ip+" | Packet Loss: "+str(sum(loss_arr))+"/"+str(all_data_len)+" | Last Ping: "+str(last_q if last_q >=0 else "Timeout"))
            timeplot.plot(x_all_data,all_data, color='blue')
            timeplot.grid(alpha=0.7)
            timeplot.relim()
            timeplot.autoscale_view()

            
            
            
            # plot timeouts
            for x, y in zip(range(1,all_data_len), all_data):
                if y < 0:
                    timeplot.axvspan(x - 0.1, x + 0.1, color='red', alpha=0.3)
                    
            zoomed1 = False
            zoomed2 = False
            # update boxplots if new packets received are over the threshold
            if new_data_count>= int(config.get('DEFAULT','boxplot_refresh_count',fallback=4)):
                
                # print(boxplot1.get_xlim())
                # print(last_lims1)

                newlim1 = boxplot1.get_xlim()
                newlim2 = boxplot2.get_xlim()

                if not is_close_tuple(boxplot1.get_xlim(),last_lims1) :
                    # print("zoomed")
                    zoomed1 = True

                if not is_close_tuple(boxplot2.get_xlim(),last_lims2) :
                    # print("zoomed")
                    zoomed2 = True
                
                # update boxplot 1
                boxplot1.clear()
                boxplot1.grid(alpha=0.7)
                boxplot1.tick_params(labelbottom=False)
                box1_dict =boxplot1.boxplot(y_data,vert=False,widths=0.7,tick_labels= ['Last '+str(y_data_len)])
                boxplot1.scatter( y_data,[1]*y_data_len, alpha=0.6, color='blue', label='Data Points')
                
                # get boxplot 1 stats
                draw_boxplot_stats(y_data,y_data_len,boxplot1,box1_dict,config)
                

                # update boxplot 2          
                boxplot2.clear()
                boxplot2.grid(alpha=0.7)
                box2_dict = boxplot2.boxplot(y_data_len1,vert=False,widths=0.7,tick_labels = ['Last '+str(y_data_len if y_data_len < len_1 else len_1 )])
                boxplot2.scatter( y_data_len1,[1]*len(y_data_len1), alpha=0.6, color='blue', label='Data Points')

                # # get boxplot 2 stats
                # stats2 = gen_boxplot_stats(y_data,y_data_len,boxplot2,box2_dict)[0]
                draw_boxplot_stats(y_data_len1,y_data_len if y_data_len < len_1 else len_1,boxplot2,box2_dict,config)
                

                rlim = max(y_data)+5
                llim = min(y_data)-1

                if not zoomed1:
                    boxplot1.set_xlim(llim,rlim)
                    last_lims1 = boxplot1.get_xlim()
                else:
                    boxplot1.set_xlim(newlim1[0],newlim1[1])

                if not zoomed2:
                    boxplot2.set_xlim(llim,rlim)
                    last_lims2 = boxplot2.get_xlim()
                else:
                    boxplot2.set_xlim(newlim2[0],newlim2[1])

        
                # if boxplot1.get_xlim()[1]>boxplot2.get_xlim()[1]:
                #     boxplot2.set_xlim(boxplot1.get_xlim())
                # else:
                #     boxplot1.set_xlim(boxplot2.get_xlim())
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
        boxplot1 = figure.add_subplot(3,1,2)
        boxplot1.clear()
        boxplot1.grid(alpha=0.7)
        boxplot1.boxplot(y_data)
        last_lims1 = boxplot1.get_xlim()

        # timeplost
        timeplot = figure.add_subplot(3,1,1)
        ping_line = timeplot.plot(x_all_data,all_data)

        # boxplot 2
        boxplot2 = figure.add_subplot(3,1,3)

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
        
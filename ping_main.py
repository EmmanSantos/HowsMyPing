from __future__ import print_function
import configparser
from icmplib import ping
import time
import multiprocessing as mp
import sys
import traceback


import matplotlib.pyplot as plt
from matplotlib.widgets import Button
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

class FigProcess(mp.Process):
    def __init__(self,y_q:mp.Queue,ip:str, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None
        self.y_q = y_q
        self.ip = ip

        self.config = configparser.ConfigParser()
        self.config.read('./config.ini')

        self.y_data=[] # ping data without timeouts
        self.y_data_len = 0 # len is incremented manually to save CPU time
        self.y_data_len1 =[] # subset of ydata containing the last len1 samples
        self.new_data_count = 0 # count for updating box plots
        self.len_1 = int(self.config.get('DEFAULT','smaller_length',fallback=20))
        self.len_2 = int(self.config.get('DEFAULT','main_length',fallback=100))
        
        self.loss_arr = [] # counting dropped packets


        self.all_data = [] # contains all ping measurements including dropped packets
        self.all_data_len = 0
        self.x_all_data = []

        self.last_lims1 = ()
        self.last_lims2 = ()
        self.autoscale_ind = True

    def run(self):
        try:
            # mp.Process.run(self)
            self.fig_create()
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    def fig_create(self):
        # init funcanimation(update)
        plt.close()
        #while loop for reopening plot window
        while True:
            #Initialize plot
            figure = plt.figure(num=1,figsize=(8,4),constrained_layout=True)
            gs = figure.add_gridspec(nrows=4, ncols=1, height_ratios=[1, 1,1,0.2])
            
            # timeplost
            # timeplot = figure.add_subplot(4,1,1)
            self.timeplot = figure.add_subplot(gs[0])
            self.ping_line = self.timeplot.plot(self.x_all_data,self.all_data)

            # boxplot 1
            # boxplot1 = figure.add_subplot(4,1,2)
            self.boxplot1 = figure.add_subplot(gs[1])
            self.boxplot1.clear()
            self.boxplot1.grid(alpha=0.7)
            self.boxplot1.boxplot(self.y_data)
            self.last_lims1 = self.boxplot1.get_xlim()

            # boxplot 2
            # boxplot2 = figure.add_subplot(4,1,3)
            self.boxplot2 = figure.add_subplot(gs[2])

            # button_plot = figure.add_subplot(4,1,4,)
            self.button_plot = figure.add_subplot(gs[3])
            # button_ax = button_plot.axes([0.1, 0.05, 0.2, 0.075])  # [left, bottom, width, height]
            self.button = Button(self.button_plot, 'Toggle Autoscale')
            self.button.on_clicked(self.toggle_autoscale)

            # plot is an animation running on a subprocess so pings continue and are not blocked by plot
            animation = FuncAnimation(figure, self.update,interval=int(self.config.get('DEFAULT','fig_refresh',fallback=500)),cache_frame_data=False)
            plt.show()
            time.sleep(0.5)
        pass
    def toggle_autoscale(self,event):
            self.autoscale_ind = not self.autoscale_ind
            print("autoscale")

    def update(self,frame):
        #Update routine that is called by FuncAnimation instance to update plot data, returns 2D tuple that is used to graph
        # nonlocal ip

        # nonlocal y_data
        # nonlocal y_data_len1
        # nonlocal new_data_count
        # nonlocal self.len_1
        # nonlocal self.len_2
        # nonlocal y_data_len
        # nonlocal loss_arr

        # nonlocal all_data
        # nonlocal all_data_len
        # nonlocal x_all_data

        # nonlocal ping_line

        # nonlocal last_lims1
        # nonlocal last_lims2
        # nonlocal autoscale_ind

        if self.y_q.empty() == False:

            # get all in queue
            while self.y_q.qsize() >0:
                last_q = self.y_q.get()
                
                # if positive packet is not dropped
                if last_q >=0:
                    self.y_data.append(last_q)

                    # append 0 to loss array  - means no packet lost
                    self.loss_arr.append(0)


                    # length is stored because len() is slow
                    if self.y_data_len < self.len_2:
                        self.y_data_len+=1

                    self.new_data_count +=1
                else:
                    # append 1 to loss array  - means packet lost
                    self.loss_arr.append(1)


                    # plot packet loss

                
                self.all_data.append(last_q)
                self.all_data_len+=1
                if self.all_data_len<=self.len_2: self.x_all_data.append(self.all_data_len) 
                

                
                

            # Caps the length of the  arrays

            if self.all_data_len >self.len_2:
                self.all_data_len = self.len_2

            # discards older data if longer than desired length
            self.y_data_len1 = self.y_data[-self.len_1:] if self.y_data_len>=self.len_1 else self.y_data
            self.y_data = self.y_data[-self.len_2:] if self.y_data_len>=self.len_2 else self.y_data
            self.loss_arr = self.loss_arr[-self.len_2:] if self.all_data_len>=self.len_2 else self.loss_arr

            self.all_data = self.all_data[-self.len_2:] if self.all_data_len>=self.len_2 else self.all_data
            
            
            # update time plot
            for artist in self.timeplot.lines:
                artist.remove()
            for patch in self.timeplot.patches[:]:
                patch.remove()
            self.timeplot.set_prop_cycle(None) 
            self.timeplot.set_title("Pinging: "+self.ip+" | Packet Loss: "+str(sum(self.loss_arr))+"/"+str(self.all_data_len)+" | Last Ping: "+str(last_q if last_q >=0 else "Timeout"))
            self.timeplot.plot(self.x_all_data,self.all_data, color='blue')
            self.timeplot.grid(alpha=0.7)
            self.timeplot.relim()
            self.timeplot.autoscale_view()

            
            
            
            # plot timeouts
            for x, y in zip(range(1,self.all_data_len), self.all_data):
                if y < 0:
                    self.timeplot.axvspan(x - 0.1, x + 0.1, color='red', alpha=0.3)
                    
            zoomed1 = False
            zoomed2 = False
            # update boxplots if new packets received are over the threshold
            if self.new_data_count>= int(self.config.get('DEFAULT','boxplot_refresh_count',fallback=4)):
                
                # print(boxplot1.get_xlim())
                # print(last_lims1)
                print(self.autoscale_ind)

                currlim1 = self.boxplot1.get_xlim()
                currlim2 = self.boxplot2.get_xlim()
                
                # update boxplot 1
                self.boxplot1.clear()
                self.boxplot1.grid(alpha=0.7)
                self.boxplot1.tick_params(labelbottom=False)
                box1_dict =self.boxplot1.boxplot(self.y_data,vert=False,widths=0.7,tick_labels= ['Last '+str(self.y_data_len)])
                self.boxplot1.scatter( self.y_data,[1]*self.y_data_len, alpha=0.6, color='blue', label='Data Points')
                
                # get boxplot 1 stats
                draw_boxplot_stats(self.y_data,self.y_data_len,self.boxplot1,box1_dict,self.config)
                

                # update boxplot 2          
                self.boxplot2.clear()
                self.boxplot2.grid(alpha=0.7)
                box2_dict = self.boxplot2.boxplot(self.y_data_len1,vert=False,widths=0.7,tick_labels = ['Last '+str(self.y_data_len if self.y_data_len < self.len_1 else self.len_1 )])
                self.boxplot2.scatter( self.y_data_len1,[1]*len(self.y_data_len1), alpha=0.6, color='blue', label='Data Points')

                # # get boxplot 2 stats
                # stats2 = gen_boxplot_stats(y_data,y_data_len,boxplot2,box2_dict)[0]
                draw_boxplot_stats(self.y_data_len1,self.y_data_len if self.y_data_len < self.len_1 else self.len_1,self.boxplot2,box2_dict,self.config)
                

                rlim = max(self.y_data)+5
                # llim = min(y_data)-1
                llim = 0

                if self.autoscale_ind:
                    self.boxplot1.set_xlim(llim,rlim)
                    self.last_lims1 = self.boxplot1.get_xlim()
                else:
                    self.boxplot1.set_xlim(currlim1[0],currlim1[1])
                    self.boxplot1.tick_params(labelbottom=True)

                if self.autoscale_ind:
                    self.boxplot2.set_xlim(llim,rlim)
                    self.last_lims2 = self.boxplot2.get_xlim()
                else:
                    self.boxplot2.set_xlim(currlim2[0],currlim2[1])

        
                # if boxplot1.get_xlim()[1]>boxplot2.get_xlim()[1]:
                #     boxplot2.set_xlim(boxplot1.get_xlim())
                # else:
                #     boxplot1.set_xlim(boxplot2.get_xlim())
                self.new_data_count = 0

        pass

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


def main():

    config = configparser.ConfigParser()
    config.read('./config.ini')
    
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = str(config.get('DEFAULT','ip',fallback='8.8.8.8'))

    data_q = mp.Queue()
    # plot_window = mp.Process(target=plot_subproc,args=[data_q,ip])
    # plot_window.start()
    plot_window = FigProcess(data_q,ip)
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
        
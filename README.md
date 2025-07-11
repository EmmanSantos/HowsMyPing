# How's My Ping?

A Python-based utility for testing ping and visualizing network latency over time using ICMP pings. The tool features real-time graphing and box plots to visualize connection quality.


<img width="873" height="514" alt="image" src="https://github.com/user-attachments/assets/7780ed2e-70ba-45f0-ae50-7ff644ab9115" />



## 🚀 Features

- **Live Ping vs Time Graph**
  - Displays response times over time.
  - **Timeouts** (missed responses) are highlighted in **red**.

- **Boxplot Analysis**
  - A full boxplot displays **all samples** in the current time window.
  - A second boxplot shows only the **most recent subset** of pings for more responsive statistics.
  - From the matplotlib documentation: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.boxplot.html
  ```
            Q1-1.5IQR   Q1   median  Q3   Q3+1.5IQR
                      |-----:-----|
      o      |--------|     :     |--------|    o  o
                      |-----:-----|
    flier             <----------->            fliers
                           IQR
  ```

    
    - Check the wiki page for more information: https://en.wikipedia.org/wiki/Box_plot 

- **Customizable via Config File**
  - Easily tweak settings without changing the code.

## How to Use
1. Download ping-tester.zip
2. Extract to any location
3. Run ping-tester.exe
4. Change config file if necessary
 
## 💻 Command Line Args
- Run using command line if for integrating with scripts that use automatic IP detection. **Arguments are prioritized** over the `config.ini`
```args
ping_tester-va.b.c.exe <ip address>
```
```args2
ping_main.py <ip address>
```
## 🛠️ Configuration

Modify the `config.ini` file with the following options:

```ini
[DEFAULT]
ip = 8.8.8.8              # IP address or domain to ping
timeout = 1               # Timeout for ping in seconds
interval = 0.5            # Interval between pings in seconds
fig_refresh = 500         # Plot refresh rate in milliseconds
main_length = 100         # Number of samples for main time graph
smaller_length = 20       # Number of samples for smaller boxplot
boxplot_refresh_count = 4 # Update boxplot every N pings

# Show/Hide Stats
mean = True
median = True
maximum = True
minimum = True

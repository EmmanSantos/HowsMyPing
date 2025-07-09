# Ping Test and Graphing Tool

A Python-based utility for visualizing network latency over time using ICMP pings. The tool features real-time graphing and statistical analysis of response times.


![image](https://github.com/user-attachments/assets/16791d57-eadd-44f0-8c20-995fb2c4f111)


## 🚀 Features

- **Live Ping vs Time Graph**
  - Displays response times over time.
  - **Timeouts** (missed responses) are highlighted in **red**.

- **Boxplot Analysis**
  - A full boxplot displays **all samples** in the current time window.
  - A second boxplot shows only the **most recent subset** of pings for more responsive statistics.

- **Customizable via Config File**
  - Easily tweak settings without changing the code.

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

import psutil
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Initialize global variables for plotting
cpu_usage = deque(maxlen=30)  # Store last 30 data points
memory_usage = deque(maxlen=30)
disk_usage = deque(maxlen=30)
time_stamps = deque(maxlen=30)

# Function to update resource usage data
def update_data():
    cpu_usage.append(psutil.cpu_percent())
    memory = psutil.virtual_memory()
    memory_usage.append(memory.percent)
    disk = psutil.disk_usage('/')
    disk_usage.append(disk.percent)
    time_stamps.append(time.strftime("%H:%M:%S"))

# Function to initialize the plots
def init_plots():
    plt.style.use('seaborn-darkgrid')
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Real-Time System Resource Monitoring", fontsize=16)

    # CPU Usage Plot
    axes[0].set_title("CPU Usage (%)")
    axes[0].set_ylim(0, 100)
    axes[0].set_ylabel("CPU (%)")
    cpu_line, = axes[0].plot([], [], label="CPU Usage", color="tab:red")

    # Memory Usage Plot
    axes[1].set_title("Memory Usage (%)")
    axes[1].set_ylim(0, 100)
    axes[1].set_ylabel("Memory (%)")
    memory_line, = axes[1].plot([], [], label="Memory Usage", color="tab:blue")

    # Disk Usage Plot
    axes[2].set_title("Disk Usage (%)")
    axes[2].set_ylim(0, 100)
    axes[2].set_ylabel("Disk (%)")
    axes[2].set_xlabel("Time")
    disk_line, = axes[2].plot([], [], label="Disk Usage", color="tab:green")

    # Add legends
    for ax in axes:
        ax.legend(loc="upper left")
    
    return fig, axes, cpu_line, memory_line, disk_line

# Function to update plots dynamically
def update_plots(frame, cpu_line, memory_line, disk_line):
    update_data()  # Update resource data
    cpu_line.set_data(range(len(cpu_usage)), cpu_usage)
    memory_line.set_data(range(len(memory_usage)), memory_usage)
    disk_line.set_data(range(len(disk_usage)), disk_usage)

    # Update time ticks
    plt.xticks(range(len(time_stamps)), time_stamps, rotation=45, ha='right')
    plt.tight_layout()
    return cpu_line, memory_line, disk_line

# Real-time Monitoring Function
def real_time_monitoring():
    fig, axes, cpu_line, memory_line, disk_line = init_plots()

    # Set the x-axis limit to the max length of data points
    for ax in axes:
        ax.set_xlim(0, 30)

    # Create animation
    ani = FuncAnimation(
        fig,
        update_plots,
        fargs=(cpu_line, memory_line, disk_line),
        interval=1000,  # Update every second
        blit=False
    )

    plt.show()

if __name__ == "__main__":
    real_time_monitoring()

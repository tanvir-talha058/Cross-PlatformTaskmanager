import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

# Initialize deques for real-time data
cpu_usage = deque([0] * 10, maxlen=60)
memory_usage = deque([0] * 10, maxlen=60)
disk_read = deque([0] * 10, maxlen=60)
disk_write = deque([0] * 10, maxlen=60)
net_sent = deque([0] * 10, maxlen=60)
net_recv = deque([0] * 10, maxlen=60)
gpu_usage = deque([0] * 10, maxlen=60)

# Update system data for real-time charts
def update_chart_data():
    while True:
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        gpu_stats = GPUtil.getGPUs()[0] if GPUtil.getGPUs() else None

        cpu_usage.append(psutil.cpu_percent())
        memory_usage.append(psutil.virtual_memory().percent)
        disk_read.append(disk_io.read_bytes / 1e6)  # Convert to MB
        disk_write.append(disk_io.write_bytes / 1e6)  # Convert to MB
        net_sent.append(net_io.bytes_sent / 1e6)  # Convert to MB
        net_recv.append(net_io.bytes_recv / 1e6)  # Convert to MB
        gpu_usage.append(gpu_stats.load * 100 if gpu_stats else 0)

        time.sleep(1)

# Processes Tab
def populate_process_table(tree):
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            tree.insert('', 'end', values=(proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], proc.info['memory_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def refresh_process_table(tree):
    tree.delete(*tree.get_children())
    populate_process_table(tree)

# Performance Tab
def update_performance_chart(canvas, axes):
    while True:
        for ax, data, title, color in axes:
            ax.clear()
            if len(data) > 0:
                ax.plot(data, label=title, color=color)
                ax.set_ylim(0, 100 if "Usage" in title else max(data) * 1.2)
            else:
                ax.set_ylim(0, 100)  # Default y-axis range for empty data
            ax.set_title(title)
            ax.legend(loc="upper right")
        canvas.draw()
        time.sleep(1)

# GPU Tab
def gpu_monitoring_label(frame):
    if GPUtil.getGPUs():
        gpu_label = ttk.Label(frame, text="GPU Usage: Updating...", style="Bold.TLabel")
        gpu_label.pack(pady=10)
        threading.Thread(target=update_gpu_label, args=(gpu_label,), daemon=True).start()
    else:
        ttk.Label(frame, text="GPU: Not Available", style="Bold.TLabel").pack(pady=10)

def update_gpu_label(label):
    while True:
        gpu = GPUtil.getGPUs()[0]
        label.config(text=f"GPU Usage: {gpu.load * 100:.2f}%")
        time.sleep(1)

# GUI Style Configuration
def configure_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Bold.TLabel", font=("Arial", 12, "bold"))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    style.configure("Treeview", font=("Arial", 10), rowheight=25)
    style.map("Treeview", background=[("selected", "#6FA3EF")])

# Main GUI
def create_task_manager():
    root = tk.Tk()
    root.title("Enhanced Task Manager Clone")
    root.geometry("1200x800")

    configure_style()

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Processes Tab
    processes_frame = ttk.Frame(notebook)
    notebook.add(processes_frame, text="Processes")

    tree = ttk.Treeview(processes_frame, columns=("PID", "Name", "CPU (%)", "Memory (%)"), show='headings', height=20)
    tree.pack(fill='both', expand=True)

    for col in ["PID", "Name", "CPU (%)", "Memory (%)"]:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    populate_process_table(tree)
    ttk.Button(processes_frame, text="Refresh", command=lambda: refresh_process_table(tree)).pack(pady=5)

    # Performance Tab
    performance_frame = ttk.Frame(notebook)
    notebook.add(performance_frame, text="Performance")

    fig = Figure(figsize=(12, 8), dpi=100)
    axes = [
        (fig.add_subplot(321), cpu_usage, "CPU Usage (%)", "tab:red"),
        (fig.add_subplot(322), memory_usage, "Memory Usage (%)", "tab:blue"),
        (fig.add_subplot(323), disk_read, "Disk Read (MB)", "tab:green"),
        (fig.add_subplot(324), disk_write, "Disk Write (MB)", "tab:orange"),
        (fig.add_subplot(325), net_sent, "Net Sent (MB)", "tab:purple"),
        (fig.add_subplot(326), net_recv, "Net Received (MB)", "tab:cyan"),
    ]
    canvas = FigureCanvasTkAgg(fig, master=performance_frame)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    threading.Thread(target=update_performance_chart, args=(canvas, axes), daemon=True).start()

    # GPU Tab
    gpu_frame = ttk.Frame(notebook)
    notebook.add(gpu_frame, text="GPU")
    gpu_monitoring_label(gpu_frame)

    # Start data update thread
    threading.Thread(target=update_chart_data, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    create_task_manager()

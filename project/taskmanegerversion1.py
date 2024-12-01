import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

# Real-time data storage
cpu_usage = deque(maxlen=60)
memory_usage = deque(maxlen=60)
timestamps = deque(maxlen=60)

# Update system data for charts
def update_chart_data():
    while True:
        cpu_usage.append(psutil.cpu_percent())
        memory = psutil.virtual_memory()
        memory_usage.append(memory.percent)
        timestamps.append(time.strftime("%H:%M:%S"))
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
def update_performance_chart(canvas, ax_cpu, ax_memory):
    while True:
        ax_cpu.clear()
        ax_memory.clear()

        ax_cpu.plot(cpu_usage, label='CPU Usage (%)', color='tab:red')
        ax_memory.plot(memory_usage, label='Memory Usage (%)', color='tab:blue')

        ax_cpu.set_title("CPU Usage")
        ax_cpu.set_ylim(0, 100)
        ax_memory.set_title("Memory Usage")
        ax_memory.set_ylim(0, 100)

        ax_cpu.legend(loc="upper right")
        ax_memory.legend(loc="upper right")

        canvas.draw()
        time.sleep(1)

# Details Tab
def show_process_details(selected_pid, details_text):
    try:
        proc = psutil.Process(int(selected_pid))
        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END, f"PID: {proc.pid}\n")
        details_text.insert(tk.END, f"Name: {proc.name()}\n")
        details_text.insert(tk.END, f"Status: {proc.status()}\n")
        details_text.insert(tk.END, f"CPU Usage: {proc.cpu_percent()}%\n")
        details_text.insert(tk.END, f"Memory Usage: {proc.memory_percent():.2f}%\n")
        details_text.insert(tk.END, f"Threads: {proc.num_threads()}\n")
    except (psutil.NoSuchProcess, ValueError):
        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END, "Process not found or invalid PID!")

# Main GUI
def create_task_manager():
    root = tk.Tk()
    root.title("Task Manager Clone")
    root.geometry("900x600")

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

    refresh_button = ttk.Button(processes_frame, text="Refresh", command=lambda: refresh_process_table(tree))
    refresh_button.pack(pady=5)

    # Performance Tab
    performance_frame = ttk.Frame(notebook)
    notebook.add(performance_frame, text="Performance")

    fig = Figure(figsize=(8, 4), dpi=100)
    ax_cpu = fig.add_subplot(211)
    ax_memory = fig.add_subplot(212)

    canvas = FigureCanvasTkAgg(fig, master=performance_frame)
    canvas.get_tk_widget().pack(fill='both', expand=True)

    threading.Thread(target=update_performance_chart, args=(canvas, ax_cpu, ax_memory), daemon=True).start()

    # Details Tab
    details_frame = ttk.Frame(notebook)
    notebook.add(details_frame, text="Details")

    pid_label = ttk.Label(details_frame, text="Enter PID:")
    pid_label.pack(pady=5)
    pid_entry = ttk.Entry(details_frame)
    pid_entry.pack(pady=5)

    details_text = tk.Text(details_frame, height=20)
    details_text.pack(fill='both', expand=True)

    details_button = ttk.Button(details_frame, text="Show Details", command=lambda: show_process_details(pid_entry.get(), details_text))
    details_button.pack(pady=5)

    # Start data update thread
    threading.Thread(target=update_chart_data, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    create_task_manager()

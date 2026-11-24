import tkinter as tk
from tkinter import ttk
import threading
import queue
import time

import psutil


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_rate(bytes_per_sec):
    return format_bytes(bytes_per_sec) + "/s"


class ProcessMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Системный монитор процессов")
        self.root.geometry("1100x600")
        self.running = True
        self.prev_io = {}
        self.interval_ms = 1000

        self.result_queue = queue.Queue()
        self.worker_thread = None

        self._build_ui()
        self._schedule_update()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        self.lbl_cpu = ttk.Label(top, text="CPU: --%", font=("Segoe UI", 10, "bold"))
        self.lbl_cpu.pack(side=tk.LEFT, padx=4)

        self.lbl_ram = ttk.Label(top, text="RAM: --%", font=("Segoe UI", 10, "bold"))
        self.lbl_ram.pack(side=tk.LEFT, padx=4)

        self.lbl_disk = ttk.Label(top, text="Диск C: --%", font=("Segoe UI", 10, "bold"))
        self.lbl_disk.pack(side=tk.LEFT, padx=4)

        self.lbl_net = ttk.Label(top, text="Сеть: --", font=("Segoe UI", 10, "bold"))
        self.lbl_net.pack(side=tk.LEFT, padx=4)

        cols = ("pid", "name", "cpu", "mem", "disk_read", "disk_write", "net_conns")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Процесс")
        self.tree.heading("cpu", text="CPU %")
        self.tree.heading("mem", text="Память МБ")
        self.tree.heading("disk_read", text="Диск чтение")
        self.tree.heading("disk_write", text="Диск запись")
        self.tree.heading("net_conns", text="Сетевые к-ции")

        self.tree.column("pid", width=60, anchor=tk.E)
        self.tree.column("name", width=260, anchor=tk.W)
        self.tree.column("cpu", width=70, anchor=tk.E)
        self.tree.column("mem", width=90, anchor=tk.E)
        self.tree.column("disk_read", width=110, anchor=tk.E)
        self.tree.column("disk_write", width=110, anchor=tk.E)
        self.tree.column("net_conns", width=90, anchor=tk.E)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree.tag_configure("high", background="#f8d7da")
        self.tree.tag_configure("med", background="#fff3cd")

        btn_frame = ttk.Frame(self.root, padding=8)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Обновить", command=self._schedule_update).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Закрыть", command=self._on_close).pack(side=tk.RIGHT, padx=4)

    def _on_close(self):
        self.running = False
        self.root.destroy()

    def _collect_data(self):
        rows = []
        new_io = {}
        now = time.time()

        try:
            cpu_total = psutil.cpu_percent(interval=0.0)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")
            net = psutil.net_io_counters()
        except Exception:
            cpu_total = 0.0
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")
            net = psutil.net_io_counters()

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pid = proc.info["pid"]
                name = proc.info["name"] or "Unknown"

                try:
                    cpu = proc.cpu_percent(interval=0.0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    cpu = 0.0

                try:
                    mem_proc = proc.memory_info().rss / (1024 * 1024)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    mem_proc = 0.0

                disk_read = 0.0
                disk_write = 0.0
                try:
                    io = proc.io_counters()
                    if pid in self.prev_io:
                        prev_read, prev_write, prev_time = self.prev_io[pid]
                        dt = max(now - prev_time, 0.001)
                        disk_read = (io.read_bytes - prev_read) / dt
                        disk_write = (io.write_bytes - prev_write) / dt
                    new_io[pid] = (io.read_bytes, io.write_bytes, now)
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    pass

                net_conns = 0
                try:
                    conns = proc.connections(kind="inet")
                    net_conns = len(conns)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                rows.append({
                    "pid": pid,
                    "name": name,
                    "cpu": cpu,
                    "mem": mem_proc,
                    "disk_read": disk_read,
                    "disk_write": disk_write,
                    "net_conns": net_conns,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        rows.sort(key=lambda r: r["cpu"], reverse=True)
        self.prev_io = new_io

        self.result_queue.put({
            "cpu_total": cpu_total,
            "mem": mem,
            "disk": disk,
            "net": net,
            "rows": rows,
        })

    def _schedule_update(self):
        if not self.running:
            return

        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._collect_data, daemon=True)
            self.worker_thread.start()

        self.root.after(100, self._poll_result)

    def _poll_result(self):
        try:
            data = self.result_queue.get_nowait()
        except queue.Empty:
            if self.running:
                self.root.after(100, self._poll_result)
            return

        try:
            self.lbl_cpu.config(text=f"CPU: {data['cpu_total']:.1f}%")
            self.lbl_ram.config(text=f"RAM: {data['mem'].percent:.1f}% ({data['mem'].used // (1024 ** 2)} MB / {data['mem'].total // (1024 ** 2)} MB)")
            self.lbl_disk.config(text=f"Диск C: {data['disk'].percent:.1f}% ({data['disk'].used // (1024 ** 2)} GB / {data['disk'].total // (1024 ** 2)} GB)")
            self.lbl_net.config(text=f"Сеть: в {format_bytes(data['net'].bytes_recv)} / вы {format_bytes(data['net'].bytes_sent)}")

            for item in self.tree.get_children():
                self.tree.delete(item)

            for r in data["rows"][:50]:
                tag = ""
                if r["cpu"] > 50:
                    tag = "high"
                elif r["cpu"] > 20:
                    tag = "med"

                self.tree.insert("", tk.END, values=(
                    r["pid"],
                    r["name"][:60],
                    f"{r['cpu']:.1f}",
                    f"{r['mem']:.1f}",
                    format_rate(r["disk_read"]),
                    format_rate(r["disk_write"]),
                    str(r["net_conns"]),
                ), tags=(tag,))
        except Exception:
            pass

        self.root.after(self.interval_ms, self._schedule_update)


def main():
    root = tk.Tk()
    app = ProcessMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

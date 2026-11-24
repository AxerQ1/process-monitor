import time
import signal
import sys

import psutil
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.box import ROUNDED

console = Console()


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_rate(bytes_per_sec):
    return format_bytes(bytes_per_sec) + "/s"


def get_process_snapshot(prev_io, prev_net, interval):
    rows = []
    new_io = {}
    new_net = {}

    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"] or "Unknown"

            try:
                cpu = proc.cpu_percent(interval=0.0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                cpu = 0.0

            try:
                mem = proc.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                mem = 0.0

            disk_read = 0.0
            disk_write = 0.0
            try:
                io = proc.io_counters()
                if pid in prev_io:
                    prev_read, prev_write, prev_time = prev_io[pid]
                    dt = max(time.time() - prev_time, 0.001)
                    disk_read = (io.read_bytes - prev_read) / dt
                    disk_write = (io.write_bytes - prev_write) / dt
                new_io[pid] = (io.read_bytes, io.write_bytes, time.time())
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                pass

            net_conns = 0
            net_sent = 0.0
            net_recv = 0.0
            try:
                conns = proc.connections(kind="inet")
                net_conns = len(conns)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            rows.append({
                "pid": pid,
                "name": name,
                "cpu": cpu,
                "mem": mem,
                "disk_read": disk_read,
                "disk_write": disk_write,
                "net_conns": net_conns,
                "net_sent": net_sent,
                "net_recv": net_recv,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    rows.sort(key=lambda r: r["cpu"], reverse=True)
    return rows, new_io


def build_table(rows):
    table = Table(box=ROUNDED, expand=True)
    table.add_column("PID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Процесс", style="magenta", no_wrap=False)
    table.add_column("CPU %", justify="right", style="green")
    table.add_column("Память МБ", justify="right", style="yellow")
    table.add_column("Диск чтение", justify="right", style="blue")
    table.add_column("Диск запись", justify="right", style="blue")
    table.add_column("Сетевые к-ции", justify="right", style="red")

    for r in rows[:30]:
        cpu_color = "green"
        if r["cpu"] > 50:
            cpu_color = "red"
        elif r["cpu"] > 20:
            cpu_color = "yellow"

        table.add_row(
            str(r["pid"]),
            r["name"][:40],
            Text(f"{r['cpu']:.1f}", style=cpu_color),
            f"{r['mem']:.1f}",
            format_rate(r["disk_read"]),
            format_rate(r["disk_write"]),
            str(r["net_conns"]),
        )

    return table


def build_header():
    cpu_total = psutil.cpu_percent(interval=0.0)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")

    cpu_bar = "#" * int(cpu_total // 2) + "-" * (50 - int(cpu_total // 2))
    mem_bar = "#" * int(mem.percent // 2) + "-" * (50 - int(mem.percent // 2))
    disk_bar = "#" * int(disk.percent // 2) + "-" * (50 - int(disk.percent // 2))

    cpu_text = Text(f"CPU: {cpu_total:.1f}%  [{cpu_bar}]", style="bold green")
    mem_text = Text(f"RAM: {mem.percent:.1f}%  [{mem_bar}] ({mem.used//(1024**2)} MB / {mem.total//(1024**2)} MB)", style="bold yellow")
    disk_text = Text(f"Disk C: {disk.percent:.1f}%  [{disk_bar}] ({disk.used//(1024**2)} GB / {disk.total//(1024**2)} GB)", style="bold blue")

    net = psutil.net_io_counters()
    net_text = Text(f"Сеть: входящий {format_bytes(net.bytes_recv)}, исходящий {format_bytes(net.bytes_sent)}", style="bold cyan")

    info = Columns([cpu_text, mem_text, disk_text, net_text], equal=True, expand=True)
    return Panel(Align.center(info), title="Системный монитор процессов", border_style="bold white")


def main():
    prev_io = {}
    interval = 1.0

    def handler(signum, frame):
        console.print("\n[bold red]Остановка монитора...[/bold red]")
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    with Live(console=console, refresh_per_second=2) as live:
        while True:
            rows, prev_io = get_process_snapshot(prev_io, {}, interval)
            table = build_table(rows)
            header = build_header()
            live.update(Columns([header, table], expand=True))
            time.sleep(interval)


if __name__ == "__main__":
    main()

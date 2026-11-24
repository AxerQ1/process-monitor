import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import json
import os
import ctypes
from ctypes import wintypes

import psutil


def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_rate(bytes_per_sec):
    return format_bytes(bytes_per_sec) + "/s"


def get_system_language():
    try:
        langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        lang_map = {
            0x0409: "en", 0x0809: "en", 0x0C09: "en", 0x1009: "en", 0x1409: "en", 0x1809: "en",
            0x1C09: "en", 0x2009: "en", 0x2409: "en", 0x2809: "en", 0x2C09: "en", 0x3009: "en",
            0x3409: "en",
            0x0419: "ru",
            0x0404: "zh", 0x0804: "zh", 0x0C04: "zh", 0x1004: "zh", 0x1404: "zh",
            0x040A: "es", 0x080A: "es", 0x0C0A: "es", 0x100A: "es", 0x140A: "es", 0x180A: "es",
            0x1C0A: "es", 0x200A: "es", 0x240A: "es", 0x280A: "es", 0x2C0A: "es", 0x300A: "es",
            0x340A: "es", 0x380A: "es", 0x3C0A: "es", 0x400A: "es", 0x440A: "es", 0x480A: "es",
            0x4C0A: "es", 0x500A: "es",
            0x0401: "ar", 0x0C01: "ar", 0x1401: "ar", 0x1801: "ar", 0x1C01: "ar", 0x2001: "ar",
            0x2401: "ar", 0x2801: "ar", 0x2C01: "ar", 0x3001: "ar", 0x3401: "ar", 0x3801: "ar",
            0x3C01: "ar",
            0x040C: "fr", 0x080C: "fr", 0x0C0C: "fr", 0x100C: "fr", 0x140C: "fr", 0x180C: "fr",
            0x0439: "hi",
            0x0416: "pt", 0x0816: "pt",
            0x0407: "de", 0x0807: "de", 0x0C07: "de", 0x1007: "de", 0x1407: "de",
            0x0411: "ja",
        }
        return lang_map.get(langid, "en")
    except Exception:
        return "en"


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


LANGUAGES = {
    "en": {
        "code": "en",
        "name": "English",
        "title": "Process Monitor",
        "tab_live": "Monitoring",
        "tab_history": "History",
        "tab_settings": "Settings",
        "cpu": "CPU",
        "ram": "RAM",
        "disk": "Disk C:",
        "network": "Network",
        "search": "Search process...",
        "pid": "PID",
        "name": "Process",
        "cpu_col": "CPU %",
        "mem": "Memory",
        "disk_read": "Disk read",
        "disk_write": "Disk write",
        "net_conns": "Connections",
        "system": "System",
        "kill_process": "Terminate Process",
        "refresh": "Refresh",
        "theme": "Theme:",
        "history": "History",
        "recording": "● RECORDING",
        "recording_off": "○ RECORDING",
        "clear_history": "Clear History",
        "export_history": "Export JSON",
        "settings": "Settings",
        "language": "Language:",
        "settings_placeholder": "Settings will appear here soon",
        "window_title": "Process Monitor",
        "cpu_time": "CPU Time (s)",
        "peak_mem": "Peak RAM (MB)",
        "disk_read_col": "Disk Read (MB)",
        "disk_write_col": "Disk Write (MB)",
        "net_total": "Network (MB)",
        "samples": "Samples",
    },
    "ru": {
        "code": "ru",
        "name": "Русский",
        "title": "Монитор процессов",
        "tab_live": "Мониторинг",
        "tab_history": "История",
        "tab_settings": "Настройки",
        "cpu": "Процессор",
        "ram": "Память",
        "disk": "Диск C:",
        "network": "Сеть",
        "search": "Поиск процесса...",
        "pid": "PID",
        "name": "Процесс",
        "cpu_col": "Проц. %",
        "mem": "Память",
        "disk_read": "Диск чт.",
        "disk_write": "Диск зап.",
        "net_conns": "Сети",
        "system": "Система",
        "kill_process": "Завершить процесс",
        "refresh": "Обновить",
        "theme": "Тема:",
        "history": "История",
        "recording": "● ЗАПИСЬ",
        "recording_off": "○ ЗАПИСЬ",
        "clear_history": "Очистить историю",
        "export_history": "Экспорт JSON",
        "settings": "Настройки",
        "language": "Язык:",
        "settings_placeholder": "Настройки скоро появятся здесь",
        "window_title": "Монитор процессов",
        "cpu_time": "Время CPU (сек)",
        "peak_mem": "Пик RAM (МБ)",
        "disk_read_col": "Диск чт. (МБ)",
        "disk_write_col": "Диск зап. (МБ)",
        "net_total": "Сеть (МБ)",
        "samples": "Записей",
    },
    "zh": {
        "code": "zh",
        "name": "中文",
        "title": "进程监视器",
        "tab_live": "监控",
        "tab_history": "历史",
        "tab_settings": "设置",
        "cpu": "CPU",
        "ram": "内存",
        "disk": "磁盘 C:",
        "network": "网络",
        "search": "搜索进程...",
        "pid": "PID",
        "name": "进程",
        "cpu_col": "CPU %",
        "mem": "内存",
        "disk_read": "磁盘读取",
        "disk_write": "磁盘写入",
        "net_conns": "连接",
        "system": "系统",
        "kill_process": "终止进程",
        "refresh": "刷新",
        "theme": "主题:",
        "history": "历史",
        "recording": "● 记录中",
        "recording_off": "○ 记录",
        "clear_history": "清除历史",
        "export_history": "导出 JSON",
        "settings": "设置",
        "language": "语言:",
        "settings_placeholder": "设置即将推出",
        "window_title": "进程监视器",
        "cpu_time": "CPU 时间 (秒)",
        "peak_mem": "峰值内存 (MB)",
        "disk_read_col": "磁盘读取 (MB)",
        "disk_write_col": "磁盘写入 (MB)",
        "net_total": "网络 (MB)",
        "samples": "样本",
    },
    "es": {
        "code": "es",
        "name": "Español",
        "title": "Monitor de Procesos",
        "tab_live": "Monitoreo",
        "tab_history": "Historia",
        "tab_settings": "Configuración",
        "cpu": "CPU",
        "ram": "RAM",
        "disk": "Disco C:",
        "network": "Red",
        "search": "Buscar proceso...",
        "pid": "PID",
        "name": "Proceso",
        "cpu_col": "CPU %",
        "mem": "Memoria",
        "disk_read": "Disco lectura",
        "disk_write": "Disco escritura",
        "net_conns": "Conexiones",
        "system": "Sistema",
        "kill_process": "Finalizar proceso",
        "refresh": "Actualizar",
        "theme": "Tema:",
        "history": "Historia",
        "recording": "● GRABANDO",
        "recording_off": "○ GRABAR",
        "clear_history": "Limpiar historial",
        "export_history": "Exportar JSON",
        "settings": "Configuración",
        "language": "Idioma:",
        "settings_placeholder": "La configuración pronto estará disponible",
        "window_title": "Monitor de Procesos",
        "cpu_time": "Tiempo CPU (s)",
        "peak_mem": "Pico RAM (MB)",
        "disk_read_col": "Disco lectura (MB)",
        "disk_write_col": "Disco escritura (MB)",
        "net_total": "Red (MB)",
        "samples": "Muestras",
    },
    "ar": {
        "code": "ar",
        "name": "العربية",
        "title": "مراقب العمليات",
        "tab_live": "المراقبة",
        "tab_history": "السجل",
        "tab_settings": "الإعدادات",
        "cpu": "وحدة المعالجة",
        "ram": "الذاكرة",
        "disk": "القرص C:",
        "network": "الشبكة",
        "search": "البحث عن عملية...",
        "pid": "معرف العملية",
        "name": "العملية",
        "cpu_col": "وحدة المعالجة %",
        "mem": "الذاكرة",
        "disk_read": "قراءة القرص",
        "disk_write": "كتابة القرص",
        "net_conns": "الاتصالات",
        "system": "النظام",
        "kill_process": "إنهاء العملية",
        "refresh": "تحديث",
        "theme": "المظهر:",
        "history": "السجل",
        "recording": "● يتم التسجيل",
        "recording_off": "○ تسجيل",
        "clear_history": "مسح السجل",
        "export_history": "تصدير JSON",
        "settings": "الإعدادات",
        "language": "اللغة:",
        "settings_placeholder": "ستظهر الإعدادات قريبًا",
        "window_title": "مراقب العمليات",
        "cpu_time": "وقت المعالجة (ثانية)",
        "peak_mem": "ذروة الذاكرة (ميجابايت)",
        "disk_read_col": "قراءة القرص (ميجابايت)",
        "disk_write_col": "كتابة القرص (ميجابايت)",
        "net_total": "الشبكة (ميجابايت)",
        "samples": "عينة",
    },
    "fr": {
        "code": "fr",
        "name": "Français",
        "title": "Moniteur de Processus",
        "tab_live": "Surveillance",
        "tab_history": "Historique",
        "tab_settings": "Paramètres",
        "cpu": "CPU",
        "ram": "RAM",
        "disk": "Disque C:",
        "network": "Réseau",
        "search": "Rechercher un processus...",
        "pid": "PID",
        "name": "Processus",
        "cpu_col": "CPU %",
        "mem": "Mémoire",
        "disk_read": "Disque lecture",
        "disk_write": "Disque écriture",
        "net_conns": "Connexions",
        "system": "Système",
        "kill_process": "Arrêter le processus",
        "refresh": "Actualiser",
        "theme": "Thème:",
        "history": "Historique",
        "recording": "● ENREGISTREMENT",
        "recording_off": "○ ENREGISTRER",
        "clear_history": "Effacer l'historique",
        "export_history": "Exporter JSON",
        "settings": "Paramètres",
        "language": "Langue:",
        "settings_placeholder": "Les paramètres seront disponibles bientôt",
        "window_title": "Moniteur de Processus",
        "cpu_time": "Temps CPU (s)",
        "peak_mem": "Pic RAM (Mo)",
        "disk_read_col": "Disque lecture (Mo)",
        "disk_write_col": "Disque écriture (Mo)",
        "net_total": "Réseau (Mo)",
        "samples": "Échantillons",
    },
    "hi": {
        "code": "hi",
        "name": "हिन्दी",
        "title": "प्रक्रिया मॉनिटर",
        "tab_live": "निगरानी",
        "tab_history": "इतिहास",
        "tab_settings": "सेटिंग्स",
        "cpu": "सीपीयू",
        "ram": "रैम",
        "disk": "डिस्क सी:",
        "network": "नेटवर्क",
        "search": "प्रक्रिया खोजें...",
        "pid": "पीआईडी",
        "name": "प्रक्रिया",
        "cpu_col": "सीपीयू %",
        "mem": "मेमोरी",
        "disk_read": "डिस्क पढ़ें",
        "disk_write": "डिस्क लिखें",
        "net_conns": "कनेक्शन",
        "system": "सिस्टम",
        "kill_process": "प्रक्रिया समाप्त करें",
        "refresh": "ताज़ा करें",
        "theme": "थीम:",
        "history": "इतिहास",
        "recording": "● रिकॉर्डिंग",
        "recording_off": "○ रिकॉर्ड",
        "clear_history": "इतिहास साफ़ करें",
        "export_history": "JSON निर्यात करें",
        "settings": "सेटिंग्स",
        "language": "भाषा:",
        "settings_placeholder": "जल्द ही सेटिंग्स आएंगी",
        "window_title": "प्रक्रिया मॉनिटर",
        "cpu_time": "सीपीयू समय (सेकंड)",
        "peak_mem": "पीक रैम (एमबी)",
        "disk_read_col": "डिस्क पढ़ें (एमबी)",
        "disk_write_col": "डिस्क लिखें (एमबी)",
        "net_total": "नेटवर्क (एमबी)",
        "samples": "नमूने",
    },
    "pt": {
        "code": "pt",
        "name": "Português",
        "title": "Monitor de Processos",
        "tab_live": "Monitoramento",
        "tab_history": "Histórico",
        "tab_settings": "Configurações",
        "cpu": "CPU",
        "ram": "RAM",
        "disk": "Disco C:",
        "network": "Rede",
        "search": "Buscar processo...",
        "pid": "PID",
        "name": "Processo",
        "cpu_col": "CPU %",
        "mem": "Memória",
        "disk_read": "Disco leitura",
        "disk_write": "Disco gravação",
        "net_conns": "Conexões",
        "system": "Sistema",
        "kill_process": "Finalizar processo",
        "refresh": "Atualizar",
        "theme": "Tema:",
        "history": "Histórico",
        "recording": "● GRAVANDO",
        "recording_off": "○ GRAVAR",
        "clear_history": "Limpar histórico",
        "export_history": "Exportar JSON",
        "settings": "Configurações",
        "language": "Idioma:",
        "settings_placeholder": "As configurações estarão disponíveis em breve",
        "window_title": "Monitor de Processos",
        "cpu_time": "Tempo CPU (s)",
        "peak_mem": "Pico RAM (MB)",
        "disk_read_col": "Disco leitura (MB)",
        "disk_write_col": "Disco gravação (MB)",
        "net_total": "Rede (MB)",
        "samples": "Amostras",
    },
    "de": {
        "code": "de",
        "name": "Deutsch",
        "title": "Prozessmonitor",
        "tab_live": "Überwachung",
        "tab_history": "Verlauf",
        "tab_settings": "Einstellungen",
        "cpu": "CPU",
        "ram": "Arbeitsspeicher",
        "disk": "Laufwerk C:",
        "network": "Netzwerk",
        "search": "Prozess suchen...",
        "pid": "PID",
        "name": "Prozess",
        "cpu_col": "CPU %",
        "mem": "Speicher",
        "disk_read": "Festplatte Lesen",
        "disk_write": "Festplatte Schreiben",
        "net_conns": "Verbindungen",
        "system": "System",
        "kill_process": "Prozess beenden",
        "refresh": "Aktualisieren",
        "theme": "Thema:",
        "history": "Verlauf",
        "recording": "● AUFNAHME",
        "recording_off": "○ AUFNEHMEN",
        "clear_history": "Verlauf löschen",
        "export_history": "JSON exportieren",
        "settings": "Einstellungen",
        "language": "Sprache:",
        "settings_placeholder": "Einstellungen werden bald verfügbar sein",
        "window_title": "Prozessmonitor",
        "cpu_time": "CPU-Zeit (Sekunden)",
        "peak_mem": "Peak RAM (MB)",
        "disk_read_col": "Festplatte Lesen (MB)",
        "disk_write_col": "Festplatte Schreiben (MB)",
        "net_total": "Netzwerk (MB)",
        "samples": "Proben",
    },
    "ja": {
        "code": "ja",
        "name": "日本語",
        "title": "プロセスモニター",
        "tab_live": "監視",
        "tab_history": "履歴",
        "tab_settings": "設定",
        "cpu": "CPU",
        "ram": "メモリ",
        "disk": "ディスク C:",
        "network": "ネットワーク",
        "search": "プロセスを検索...",
        "pid": "PID",
        "name": "プロセス",
        "cpu_col": "CPU %",
        "mem": "メモリ",
        "disk_read": "ディスク読み取り",
        "disk_write": "ディスク書き込み",
        "net_conns": "接続",
        "system": "システム",
        "kill_process": "プロセスを終了",
        "refresh": "更新",
        "theme": "テーマ:",
        "history": "履歴",
        "recording": "● 録画中",
        "recording_off": "○ 録画",
        "clear_history": "履歴をクリア",
        "export_history": "JSON をエクスポート",
        "settings": "設定",
        "language": "言語:",
        "settings_placeholder": "設定は間もなく公開されます",
        "window_title": "プロセスモニター",
        "cpu_time": "CPU 時間 (秒)",
        "peak_mem": "ピーク メモリ (MB)",
        "disk_read_col": "ディスク読み取り (MB)",
        "disk_write_col": "ディスク書き込み (MB)",
        "net_total": "ネットワーク (MB)",
        "samples": "サンプル",
    },
}


THEMES = {
    "dark": {
        "bg": "#0f172a",
        "surface": "#1e293b",
        "surface_hover": "#334155",
        "panel_bg": "#1e293b",
        "fg": "#f8fafc",
        "fg_secondary": "#94a3b8",
        "tree_bg": "#1e293b",
        "tree_fg": "#f8fafc",
        "heading_bg": "#0f172a",
        "heading_fg": "#cbd5e1",
        "accent": "#3b82f6",
        "accent_hover": "#60a5fa",
        "danger": "#ef4444",
        "danger_hover": "#f87171",
        "success": "#22c55e",
        "success_hover": "#4ade80",
        "high": "#450a0a",
        "med": "#4d3d08",
        "toggle_on": "#3b82f6",
        "toggle_off": "#64748b",
        "toggle_thumb": "#ffffff",
        "border": "#334155",
        "shadow": "#0000004d",
    },
}


HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=36, style="accent", **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.style = style
        self.colors = None
        self.is_hovered = False
        self._bind_events()
        self._draw()

    def set_colors(self, colors):
        self.colors = colors
        self._draw()

    def _bind_events(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, event):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event):
        self.is_hovered = False
        self._draw()

    def _on_click(self, event):
        self._draw(pressed=True)

    def _on_release(self, event):
        self._draw()
        if self.command:
            self.command()

    def _get_style_colors(self):
        c = self.colors or {"accent": "#3b82f6", "danger": "#ef4444", "success": "#22c55e", "fg": "#ffffff", "surface": "#1e293b", "border": "#e5e7eb"}
        styles = {
            "accent": (c["accent"], c.get("accent_hover", c["accent"]), c["fg"]),
            "danger": (c["danger"], c.get("danger_hover", c["danger"]), c["fg"]),
            "success": (c["success"], c.get("success_hover", c["success"]), c["fg"]),
            "ghost": (c["surface"], c.get("surface_hover", c["surface"]), c["fg"]),
        }
        return styles.get(self.style, styles["accent"])

    def _draw(self, pressed=False):
        self.delete("all")
        if not self.colors:
            return
        base_color, hover_color, text_color = self._get_style_colors()
        color = hover_color if self.is_hovered else base_color
        if pressed:
            r = max(0, int(color[1:3], 16) - 20)
            g = max(0, int(color[3:5], 16) - 20)
            b = max(0, int(color[5:7], 16) - 20)
            color = f"#{r:02x}{g:02x}{b:02x}"

        r = 8
        self.create_rounded_rect(2, 2, self.width - 2, self.height - 2, r, fill=color, outline="")
        self.create_text(
            self.width // 2,
            self.height // 2,
            text=self.text,
            fill=text_color,
            font=("Segoe UI", 9, "bold"),
        )

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class StatCard(tk.Frame):
    def __init__(self, parent, title, value, unit, colors, **kwargs):
        super().__init__(parent, bg=colors["surface"], highlightthickness=0, **kwargs)
        self.colors = colors
        self.title_label = tk.Label(
            self, text=title, bg=colors["surface"], fg=colors["fg_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        self.title_label.pack(anchor=tk.W, padx=16, pady=(14, 2))
        self.value_label = tk.Label(
            self, text=f"{value}{unit}", bg=colors["surface"], fg=colors["fg"],
            font=("Segoe UI", 16, "bold"),
        )
        self.value_label.pack(anchor=tk.W, padx=16, pady=(0, 14))
        self.configure(width=200, height=90)
        self.pack_propagate(False)

    def update_value(self, value, unit=""):
        self.value_label.config(text=f"{value}{unit}")


class ThemeToggle(tk.Canvas):
    def __init__(self, parent, theme_colors, command=None, **kwargs):
        super().__init__(parent, width=44, height=22, highlightthickness=0, bg=theme_colors["bg"], **kwargs)
        self.theme_colors = theme_colors
        self.command = command
        self.is_on = False
        self._x_on = 30
        self._x_off = 14
        self._x = self._x_off
        self._bind_events()
        self._draw()

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))

    def _draw(self):
        self.delete("all")
        c = self.theme_colors
        track_color = c["toggle_on"] if self.is_on else c["toggle_off"]
        self.create_rounded_rect(2, 2, 42, 20, 10, fill=track_color, outline="")
        thumb_x = self._x_on if self.is_on else self._x_off
        self.create_oval(
            thumb_x - 8, 3, thumb_x + 8, 19,
            fill=c["toggle_thumb"], outline="#999999", width=1,
        )

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, event):
        self.is_on = not self.is_on
        steps = 10
        start = self._x_off if not self.is_on else self._x_on
        end = self._x_on if self.is_on else self._x_off
        for i in range(steps + 1):
            self._x = start + (end - start) * i / steps
            self._draw()
            self.update()
            time.sleep(0.01)
        self._x = end
        self._draw()
        if self.command:
            self.command(self.is_on)

    def set_on(self, value):
        self.is_on = value
        self._x = self._x_on if value else self._x_off
        self._draw()


class RecordToggle(tk.Canvas):
    def __init__(self, parent, colors, command=None, **kwargs):
        super().__init__(parent, width=100, height=32, highlightthickness=0, bg=colors["surface"], **kwargs)
        self.colors = colors
        self.command = command
        self.recording = False
        self._bind_events()
        self._draw()

    def set_colors(self, colors):
        self.colors = colors
        self._draw()

    def _bind_events(self):
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda e: self.config(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.config(cursor=""))

    def _draw(self):
        self.delete("all")
        c = self.colors
        if self.recording:
            bg_color = c["danger"]
            dot_color = "#ffffff"
            text_color = "#ffffff"
            text = "● ЗАПИСЬ"
        else:
            bg_color = c["surface_hover"]
            dot_color = c["fg_secondary"]
            text_color = c["fg_secondary"]
            text = "○ ЗАПИСЬ"

        self.create_rounded_rect(2, 2, 98, 30, 15, fill=bg_color, outline="")
        self.create_oval(7, 7, 21, 21, fill=dot_color, outline="")
        self.create_text(55, 16, text=text, fill=text_color, font=("Segoe UI", 9, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_click(self, event):
        self.recording = not self.recording
        self._draw()
        if self.command:
            self.command(self.recording)

    def set_recording(self, value):
        self.recording = value
        self._draw()


class ProcessMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Monitor")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)
        self.root.overrideredirect(True)
        self._set_rounded_corners()

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.running = True
        self.prev_io = {}
        self.interval_ms = 1000

        self.result_queue = queue.Queue()
        self.worker_thread = None
        self.all_rows = []
        self.tree_pid_map = {}

        self.theme = "dark"
        self.colors = THEMES[self.theme]

        # Language state
        self.config_data = load_config()
        saved_lang = self.config_data.get("language")
        if saved_lang and saved_lang in LANGUAGES:
            self.language = saved_lang
        else:
            self.language = get_system_language()
        self.lang = LANGUAGES[self.language]

        # History state
        self.recording = False
        self.history_data = load_history()
        self.history_samples = 0

        self._set_rounded_corners()
        self._build_ui()
        self._apply_theme()
        self._schedule_update()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_rounded_corners(self):
        try:
            hwnd = self.root.winfo_id()
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)), 4,
            )
        except Exception:
            try:
                hwnd = self.root.winfo_id()
                user32 = ctypes.windll.user32
                gdi32 = ctypes.windll.gdi32
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                rgn = gdi32.CreateRoundRectRgn(0, 0, width, height, 20, 20)
                user32.SetWindowRgn(hwnd, rgn, True)
            except Exception:
                pass

    def _build_ui(self):
        self.root.configure(bg=self.colors["bg"])

        self.title_bar = tk.Frame(self.root, bg=self.colors["surface"], height=48, highlightthickness=0)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)

        self.lbl_title = tk.Label(
            self.title_bar,
            text="Process Monitor",
            bg=self.colors["surface"],
            fg=self.colors["fg"],
            font=("Segoe UI", 13, "bold"),
        )
        self.lbl_title.pack(side=tk.LEFT, padx=20, pady=12)

        btn_close = tk.Button(
            self.title_bar,
            text="✕",
            bg=self.colors["surface"],
            fg=self.colors["fg"],
            activebackground=self.colors["danger"],
            activeforeground="#ffffff",
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            command=self._on_close,
            cursor="hand2",
        )
        btn_close.pack(side=tk.RIGHT, padx=12, pady=10)

        btn_min = tk.Button(
            self.title_bar,
            text="—",
            bg=self.colors["surface"],
            fg=self.colors["fg"],
            activebackground=self.colors["surface_hover"],
            activeforeground=self.colors["fg"],
            borderwidth=0,
            font=("Segoe UI", 14),
            command=self.root.iconify,
            cursor="hand2",
        )
        btn_min.pack(side=tk.RIGHT, padx=4, pady=10)

        self.title_bar.bind("<Button-1>", self._start_drag)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        self.lbl_title.bind("<Button-1>", self._start_drag)
        self.lbl_title.bind("<B1-Motion>", self._on_drag)

        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Tab notebook
        self.notebook = ttk.Notebook(main_container, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Live monitoring
        self.tab_live = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_live, text="Мониторинг")

        stats_row = tk.Frame(self.tab_live, bg=self.colors["bg"])
        stats_row.pack(fill=tk.X, pady=(0, 16))

        self.card_cpu = StatCard(stats_row, "CPU", "0.0", "%", self.colors)
        self.card_cpu.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

        self.card_ram = StatCard(stats_row, "RAM", "0.0", "%", self.colors)
        self.card_ram.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

        self.card_disk = StatCard(stats_row, "Диск C:", "0.0", "%", self.colors)
        self.card_disk.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

        self.card_net = StatCard(stats_row, "Сеть", "0.00", " MB/s", self.colors)
        self.card_net.pack(side=tk.LEFT, fill=tk.X, expand=True)

        content = tk.Frame(self.tab_live, bg=self.colors["bg"])
        content.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(content, bg=self.colors["surface"], highlightbackground=self.colors["border"], highlightthickness=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        search_frame = tk.Frame(left_panel, bg=self.colors["surface"])
        search_frame.pack(fill=tk.X, padx=16, pady=14)

        search_label = tk.Label(
            search_frame, text="🔍", bg=self.colors["surface"], fg=self.colors["fg_secondary"],
            font=("Segoe UI", 11),
        )
        search_label.pack(side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=30,
            relief="flat",
            bg=self.colors["tree_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._schedule_update())
        self.search_entry.insert(0, "Поиск процесса...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Поиск процесса..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "Поиск процесса...") if not self.search_entry.get() else None)

        cols = ("pid", "name", "cpu", "mem", "disk_read", "disk_write", "net_conns")
        self.tree = ttk.Treeview(left_panel, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Процесс")
        self.tree.heading("cpu", text="CPU %")
        self.tree.heading("mem", text="Память")
        self.tree.heading("disk_read", text="Диск чт.")
        self.tree.heading("disk_write", text="Диск зап.")
        self.tree.heading("net_conns", text="Сети")

        self.tree.column("pid", width=60, anchor=tk.E)
        self.tree.column("name", width=240, anchor=tk.W)
        self.tree.column("cpu", width=70, anchor=tk.E)
        self.tree.column("mem", width=90, anchor=tk.E)
        self.tree.column("disk_read", width=90, anchor=tk.E)
        self.tree.column("disk_write", width=90, anchor=tk.E)
        self.tree.column("net_conns", width=60, anchor=tk.E)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.tree.tag_configure("high", background=self.colors["high"])
        self.tree.tag_configure("med", background=self.colors["med"])

        right_panel = tk.Frame(content, bg=self.colors["surface"], width=280, highlightbackground=self.colors["border"], highlightthickness=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        info_header = tk.Frame(right_panel, bg=self.colors["surface"])
        info_header.pack(fill=tk.X, padx=16, pady=(16, 12))
        tk.Label(
            info_header, text="Система", bg=self.colors["surface"], fg=self.colors["fg"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT)

        self.sys_info = tk.Frame(right_panel, bg=self.colors["surface"])
        self.sys_info.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.lbl_sys_cpu = tk.Label(self.sys_info, text="CPU: 0.0%", bg=self.colors["surface"], fg=self.colors["fg_secondary"], font=("Segoe UI", 10))
        self.lbl_sys_cpu.pack(anchor=tk.W, pady=2)

        self.lbl_sys_ram = tk.Label(self.sys_info, text="RAM: 0.0%", bg=self.colors["surface"], fg=self.colors["fg_secondary"], font=("Segoe UI", 10))
        self.lbl_sys_ram.pack(anchor=tk.W, pady=2)

        self.lbl_sys_disk = tk.Label(self.sys_info, text="Диск: 0.0%", bg=self.colors["surface"], fg=self.colors["fg_secondary"], font=("Segoe UI", 10))
        self.lbl_sys_disk.pack(anchor=tk.W, pady=2)

        self.lbl_sys_net = tk.Label(self.sys_info, text="Сеть: 0.00 MB/s", bg=self.colors["surface"], fg=self.colors["fg_secondary"], font=("Segoe UI", 10))
        self.lbl_sys_net.pack(anchor=tk.W, pady=2)

        actions = tk.Frame(right_panel, bg=self.colors["surface"])
        actions.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.btn_kill = ModernButton(actions, text="Завершить процесс", command=self._kill_selected_process, width=200, height=36, style="danger")
        self.btn_kill.pack(pady=4)
        self.btn_kill.set_colors(self.colors)

        self.btn_refresh = ModernButton(actions, text="Обновить", command=self._schedule_update, width=200, height=36, style="ghost")
        self.btn_refresh.pack(pady=4)
        self.btn_refresh.set_colors(self.colors)

        # Tab 2: History
        self.tab_history = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_history, text="История")

        history_header = tk.Frame(self.tab_history, bg=self.colors["bg"])
        history_header.pack(fill=tk.X, padx=16, pady=(16, 12))

        self.record_toggle = RecordToggle(history_header, self.colors, command=self._toggle_recording)
        self.record_toggle.pack(side=tk.LEFT, padx=(0, 16))

        btn_clear_hist = ModernButton(history_header, text="Очистить историю", command=self._clear_history, width=140, height=36, style="danger")
        btn_clear_hist.pack(side=tk.LEFT, padx=4)
        btn_clear_hist.set_colors(self.colors)

        btn_export_hist = ModernButton(history_header, text="Экспорт JSON", command=self._export_history, width=140, height=36, style="ghost")
        btn_export_hist.pack(side=tk.LEFT, padx=4)
        btn_export_hist.set_colors(self.colors)

        hist_cols = ("pid", "name", "cpu_time", "peak_mem", "disk_read", "disk_write", "net_total", "samples")
        self.hist_tree = ttk.Treeview(self.tab_history, columns=hist_cols, show="headings", selectmode="browse")
        self.hist_tree.heading("pid", text="PID")
        self.hist_tree.heading("name", text="Процесс")
        self.hist_tree.heading("cpu_time", text="CPU время (сек)")
        self.hist_tree.heading("peak_mem", text="Пик RAM (МБ)")
        self.hist_tree.heading("disk_read", text="Диск чт. (МБ)")
        self.hist_tree.heading("disk_write", text="Диск зап. (МБ)")
        self.hist_tree.heading("net_total", text="Сеть (МБ)")
        self.hist_tree.heading("samples", text="Записей")

        self.hist_tree.column("pid", width=60, anchor=tk.E)
        self.hist_tree.column("name", width=220, anchor=tk.W)
        self.hist_tree.column("cpu_time", width=90, anchor=tk.E)
        self.hist_tree.column("peak_mem", width=90, anchor=tk.E)
        self.hist_tree.column("disk_read", width=100, anchor=tk.E)
        self.hist_tree.column("disk_write", width=100, anchor=tk.E)
        self.hist_tree.column("net_total", width=90, anchor=tk.E)
        self.hist_tree.column("samples", width=70, anchor=tk.E)

        self.hist_tree.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.hist_tree.tag_configure("high", background=self.colors["high"])
        self.hist_tree.tag_configure("med", background=self.colors["med"])

        self._refresh_history_table()

        # Tab 3: Settings
        self.tab_settings = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(self.tab_settings, text=self.lang["tab_settings"])

        settings_container = tk.Frame(self.tab_settings, bg=self.colors["bg"])
        settings_container.pack(fill=tk.X, padx=40, pady=40)

        lang_label = tk.Label(
            settings_container,
            text=self.lang["language"],
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 12, "bold"),
        )
        lang_label.pack(side=tk.LEFT, padx=(0, 16))

        self.language_var = tk.StringVar(value=self.lang["name"])
        self.language_combo = ttk.Combobox(
            settings_container,
            textvariable=self.language_var,
            values=[LANGUAGES[code]["name"] for code in LANGUAGES],
            state="readonly",
            width=25,
            font=("Segoe UI", 11),
        )
        self.language_combo.pack(side=tk.LEFT)
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        settings_note = tk.Label(
            self.tab_settings,
            text=self.lang["settings_placeholder"],
            bg=self.colors["bg"],
            fg=self.colors["fg_secondary"],
            font=("Segoe UI", 11),
        )
        settings_note.pack(pady=40)

        self.settings_note_label = settings_note
        self.lang_label_widget = lang_label

    def _toggle_recording(self, recording):
        self.recording = recording
        self.record_toggle.set_recording(recording)
        if recording:
            self.history_samples = 0

    def _on_language_change(self, event=None):
        selected_name = self.language_var.get()
        for code, lang_data in LANGUAGES.items():
            if lang_data["name"] == selected_name:
                self.language = code
                self.lang = LANGUAGES[code]
                self.config_data["language"] = code
                save_config(self.config_data)
                self._apply_language()
                break

    def _apply_language(self):
        lang = self.lang
        self.root.title(lang["window_title"])

        # Update tab names
        self.notebook.tab(self.tab_live, text=lang["tab_live"])
        self.notebook.tab(self.tab_history, text=lang["tab_history"])
        self.notebook.tab(self.tab_settings, text=lang["tab_settings"])

        # Update stat card titles
        if hasattr(self, "card_cpu"):
            self.card_cpu.title_label.config(text=lang["cpu"])
        if hasattr(self, "card_ram"):
            self.card_ram.title_label.config(text=lang["ram"])
        if hasattr(self, "card_disk"):
            self.card_disk.title_label.config(text=lang["disk"])
        if hasattr(self, "card_net"):
            self.card_net.title_label.config(text=lang["network"])

        # Update tree headings (live)
        self.tree.heading("pid", text=lang["pid"])
        self.tree.heading("name", text=lang["name"])
        self.tree.heading("cpu", text=lang["cpu_col"])
        self.tree.heading("mem", text=lang["mem"])
        self.tree.heading("disk_read", text=lang["disk_read"])
        self.tree.heading("disk_write", text=lang["disk_write"])
        self.tree.heading("net_conns", text=lang["net_conns"])

        # Update search placeholder
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, lang["search"])

        # Update buttons
        if hasattr(self, "btn_kill"):
            self.btn_kill.text = lang["kill_process"]
            self.btn_kill._draw()
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.text = lang["refresh"]
            self.btn_refresh._draw()

        # Update history tree headings
        self.hist_tree.heading("pid", text=lang["pid"])
        self.hist_tree.heading("name", text=lang["name"])
        self.hist_tree.heading("cpu_time", text=lang["cpu_time"])
        self.hist_tree.heading("peak_mem", text=lang["peak_mem"])
        self.hist_tree.heading("disk_read", text=lang["disk_read_col"])
        self.hist_tree.heading("disk_write", text=lang["disk_write_col"])
        self.hist_tree.heading("net_total", text=lang["net_total"])
        self.hist_tree.heading("samples", text=lang["samples"])

        # Update settings tab
        if hasattr(self, "lang_label_widget"):
            self.lang_label_widget.config(text=lang["language"])
        if hasattr(self, "settings_note_label"):
            self.settings_note_label.config(text=lang["settings_placeholder"])

        # Update history buttons
        if hasattr(self, "record_toggle"):
            self.record_toggle._draw()
        self._refresh_history_table()

    def _clear_history(self):
        self.history_data = {}
        self.history_samples = 0
        save_history({})
        self._refresh_history_table()

    def _export_history(self):
        try:
            export_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history_export.json")
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _refresh_history_table(self):
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)

        for pid_str, data in sorted(self.history_data.items(), key=lambda x: x[1].get("cpu_time", 0), reverse=True):
            tag = ""
            cpu_time = data.get("cpu_time", 0)
            if cpu_time > 100:
                tag = "high"
            elif cpu_time > 30:
                tag = "med"

            self.hist_tree.insert("", tk.END, values=(
                pid_str,
                data.get("name", "Unknown")[:50],
                f"{cpu_time:.1f}",
                f"{data.get('peak_mem', 0):.1f}",
                f"{data.get('disk_read', 0) / (1024 * 1024):.2f}",
                f"{data.get('disk_write', 0) / (1024 * 1024):.2f}",
                f"{(data.get('net_sent', 0) + data.get('net_recv', 0)) / (1024 * 1024):.2f}",
                data.get("samples", 0),
            ), tags=(tag,))

    def _apply_theme(self):
        c = self.colors
        self.root.configure(bg=c["bg"])
        self.title_bar.configure(bg=c["surface"])
        self.lbl_title.configure(bg=c["surface"], fg=c["fg"])

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])

        style.configure(
            "Treeview",
            background=c["tree_bg"],
            foreground=c["tree_fg"],
            fieldbackground=c["tree_bg"],
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            insertbackground=c["tree_fg"],
        )
        style.configure(
            "Treeview.Heading",
            background=c["heading_bg"],
            foreground=c["heading_fg"],
            borderwidth=0,
            relief="flat",
        )
        style.map("Treeview", background=[("selected", c["accent"])])
        style.map("Treeview.Heading", background=[("active", c["heading_bg"])])

        style.configure(
            "TNotebook",
            background=c["bg"],
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=c["surface"],
            foreground=c["fg_secondary"],
            borderwidth=0,
            padding=[16, 8],
            font=("Segoe UI", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", c["surface_hover"])],
            foreground=[("selected", c["fg"])],
        )

        self.tree.tag_configure("high", background=c["high"])
        self.tree.tag_configure("med", background=c["med"])
        self.hist_tree.tag_configure("high", background=c["high"])
        self.hist_tree.tag_configure("med", background=c["med"])

        if hasattr(self, "card_cpu"):
            self.card_cpu.configure(bg=c["surface"])
            self.card_cpu.title_label.configure(bg=c["surface"], fg=c["fg_secondary"])
            self.card_cpu.value_label.configure(bg=c["surface"], fg=c["fg"])

        if hasattr(self, "card_ram"):
            self.card_ram.configure(bg=c["surface"])
            self.card_ram.title_label.configure(bg=c["surface"], fg=c["fg_secondary"])
            self.card_ram.value_label.configure(bg=c["surface"], fg=c["fg"])

        if hasattr(self, "card_disk"):
            self.card_disk.configure(bg=c["surface"])
            self.card_disk.title_label.configure(bg=c["surface"], fg=c["fg_secondary"])
            self.card_disk.value_label.configure(bg=c["surface"], fg=c["fg"])

        if hasattr(self, "card_net"):
            self.card_net.configure(bg=c["surface"])
            self.card_net.title_label.configure(bg=c["surface"], fg=c["fg_secondary"])
            self.card_net.value_label.configure(bg=c["surface"], fg=c["fg"])

        if hasattr(self, "btn_kill"):
            self.btn_kill.set_colors(c)
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.set_colors(c)
        if hasattr(self, "record_toggle"):
            self.record_toggle.set_colors(c)

        self._apply_language()

    def _start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}

    def _on_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    def _on_close(self):
        self.running = False
        self.config_data["language"] = self.language
        save_config(self.config_data)
        save_history(self.history_data)
        self.root.destroy()

    def _kill_selected_process(self):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        pid = self.tree_pid_map.get(item_id)
        if not pid:
            return

        try:
            proc = psutil.Process(pid)
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

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

                # Accumulate history if recording
                if self.recording:
                    pid_str = str(pid)
                    if pid_str not in self.history_data:
                        self.history_data[pid_str] = {
                            "name": name,
                            "cpu_time": 0.0,
                            "peak_mem": 0.0,
                            "disk_read": 0.0,
                            "disk_write": 0.0,
                            "net_sent": 0,
                            "net_recv": 0,
                            "samples": 0,
                            "first_seen": now,
                            "last_seen": now,
                        }

                    h = self.history_data[pid_str]
                    h["cpu_time"] += cpu * (self.interval_ms / 1000.0) / 100.0
                    h["peak_mem"] = max(h["peak_mem"], mem_proc)
                    h["disk_read"] += disk_read * (self.interval_ms / 1000.0)
                    h["disk_write"] += disk_write * (self.interval_ms / 1000.0)
                    h["net_sent"] += net.bytes_sent
                    h["net_recv"] += net.bytes_recv
                    h["samples"] += 1
                    h["last_seen"] = now
                    h["name"] = name

                    self.history_samples += 1

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
            "recording": self.recording,
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
            c = self.colors

            self.card_cpu.update_value(f"{data['cpu_total']:.1f}", "%")
            self.card_ram.update_value(f"{data['mem'].percent:.1f}", "%")
            self.card_disk.update_value(f"{data['disk'].percent:.1f}", "%")
            net_speed = (data['net'].bytes_recv + data['net'].bytes_sent) / (1024 * 1024)
            self.card_net.update_value(f"{net_speed:.2f}", " MB/s")

            self.lbl_sys_cpu.config(text=f"CPU: {data['cpu_total']:.1f}%")
            self.lbl_sys_ram.config(text=f"RAM: {data['mem'].percent:.1f}%")
            self.lbl_sys_disk.config(text=f"Диск: {data['disk'].percent:.1f}%")
            self.lbl_sys_net.config(text=f"Сеть: {net_speed:.2f} MB/s")

            for item in self.tree.get_children():
                self.tree.delete(item)

            self.tree_pid_map = {}

            search_term = self.search_var.get().strip().lower()
            if search_term == "поиск процесса...":
                search_term = ""

            filtered_rows = []
            for r in data["rows"]:
                if search_term:
                    if search_term in str(r["pid"]) or search_term in r["name"].lower():
                        filtered_rows.append(r)
                else:
                    filtered_rows.append(r)

            for r in filtered_rows[:50]:
                tag = ""
                if r["cpu"] > 50:
                    tag = "high"
                elif r["cpu"] > 20:
                    tag = "med"

                item_id = self.tree.insert("", tk.END, values=(
                    r["pid"],
                    r["name"][:60],
                    f"{r['cpu']:.1f}",
                    f"{r['mem']:.1f}",
                    format_rate(r["disk_read"]),
                    format_rate(r["disk_write"]),
                    str(r["net_conns"]),
                ), tags=(tag,))
                self.tree_pid_map[item_id] = r["pid"]

            # Refresh history table periodically
            if data.get("recording"):
                self.root.after_idle(self._refresh_history_table)

        except Exception as e:
            print("UI update error:", e)

        self.root.after(self.interval_ms, self._schedule_update)


def main():
    try:
        root = tk.Tk()
        app = ProcessMonitorApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        import tkinter.messagebox as msgbox
        root = tk.Tk()
        root.withdraw()
        msgbox.showerror("Ошибка запуска", f"{e}\n\n{traceback.format_exc()}")
        root.destroy()


if __name__ == "__main__":
    main()

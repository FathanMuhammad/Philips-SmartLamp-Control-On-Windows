import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox
import colorsys

# ==============================
# KONFIGURASI
# ==============================
PORT = 38899
TARGET_MACS = {
    "A8BB50B5A2E9": "Lampu Meja",
    "CC40858E7E82": "Lampu LED Strip"
}


# ==============================
# DISCOVERY
# ==============================
def discover_lamps(timeout=2):
    found = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    msg = json.dumps({"method": "getSystemConfig", "params": {}})
    sock.sendto(msg.encode(), ('255.255.255.255', PORT))

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            try:
                js = json.loads(data.decode())
                mac = js.get("result", {}).get("mac", "").upper()
                if mac in TARGET_MACS:
                    found[mac] = ip
            except:
                continue
    except socket.timeout:
        pass

    sock.close()
    return found


# ==============================
# FUNGSI KIRIM / AMBIL STATUS
# ==============================
def kirim_perintah(ip, command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.sendto(json.dumps(command).encode(), (ip, PORT))
        sock.close()
    except Exception as e:
        messagebox.showerror("Error", f"Gagal kirim ke {ip}\n{e}")


def get_status(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        message = json.dumps({"method": "getPilot"})
        sock.sendto(message.encode(), (ip, PORT))
        data, _ = sock.recvfrom(1024)
        sock.close()
        return json.loads(data.decode())
    except Exception as e:
        print(f"Gagal ambil status dari {ip}: {e}")
        return {}


# ==============================
# FUNGSI KONTROL
# ==============================
def lamp_on(ip, status_label=None):
    kirim_perintah(ip, {"method": "setState", "params": {"state": True}})
    if status_label:
        status_label.config(text="🟢 Lampu Menyala", fg="lime")


def lamp_off(ip, status_label=None):
    kirim_perintah(ip, {"method": "setState", "params": {"state": False}})
    if status_label:
        status_label.config(text="🔴 Lampu Mati", fg="red")


def lamp_brightness(ip, value):
    value = int(float(value))
    kirim_perintah(ip, {"method": "setPilot", "params": {"dimming": value}})


def lamp_kelvin(ip, value):
    value = int(float(value))
    kirim_perintah(ip, {"method": "setPilot", "params": {"temp": value}})


def lamp_rgb(ip, r, g, b):
    kirim_perintah(ip, {"method": "setPilot", "params": {"r": r, "g": g, "b": b}})


# ==============================
# KONVERSI WARNA
# ==============================
def kelvin_to_hex(k):
    ratio = (k - 2000) / (6500 - 2000)
    r = int(255)
    g = int(180 + (255 - 180) * ratio)
    b = int(100 + (255 - 100) * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


def hue_to_rgb(hue):
    h = hue / 360
    r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
    return int(r * 255), int(g * 255), int(b * 255)


# ==============================
# WIDGET HUE SLIDER
# ==============================
class HueSlider(tk.Canvas):
    def __init__(self, parent, ip, height=25, **kwargs):
        super().__init__(parent, height=height, **kwargs)
        self.ip = ip
        self.height = height
        self.indicator = None
        self.hue = 0
        self.width = 300

        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.width = event.width
        self.draw_gradient()
        self.draw_indicator()

    def draw_gradient(self):
        self.delete("gradient")
        steps = self.width
        for x in range(steps):
            hue = (x / steps) * 360
            r, g, b = hue_to_rgb(hue)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(x, 0, x, self.height, fill=color, tags="gradient")

    def draw_indicator(self):
        if self.indicator:
            self.delete(self.indicator)
        x = int((self.hue / 360) * self.width)
        y0, y1 = 0, self.height
        radius = 6
        self.indicator = self.create_oval(x - radius, y0, x + radius, y1, outline="white", width=2)

    def update_hue(self, x):
        x = max(0, min(self.width, x))
        self.hue = (x / self.width) * 360
        r, g, b = hue_to_rgb(self.hue)
        lamp_rgb(self.ip, r, g, b)
        self.draw_indicator()

    def click(self, event):
        self.update_hue(event.x)

    def drag(self, event):
        self.update_hue(event.x)


# ==============================
# SINKRON UI
# ==============================
def sync_ui(ip, bright_slider, kelvin_slider, preview, status_label, hue_slider):
    status = get_status(ip)
    if "result" in status:
        result = status["result"]

        if "state" in result:
            if result["state"]:
                status_label.config(text="🟢 Lampu Menyala", fg="lime")
            else:
                status_label.config(text="🔴 Lampu Mati", fg="red")

        if "dimming" in result:
            bright_slider.set(result["dimming"])

        if "temp" in result:
            kelvin_slider.set(result["temp"])
            preview.configure(bg=kelvin_to_hex(result["temp"]))

        if all(k in result for k in ("r", "g", "b")):
            r, g, b = result["r"], result["g"], result["b"]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            hue_slider.hue = h * 360
            hue_slider.draw_indicator()


# ==============================
# UI
# ==============================
root = tk.Tk()
root.title("WiZ Lamp Controller")
root.configure(bg="#2b2b2b")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=4, relief="flat")
style.map("TButton", background=[("active", "#4a90e2")], foreground=[("active", "white")])
style.configure("TLabel", background="#2b2b2b", foreground="white", font=("Segoe UI", 9))
style.configure("TLabelframe", background="#3c3f41", foreground="white", font=("Segoe UI", 11, "bold"))
style.configure("TLabelframe.Label", background="#3c3f41", foreground="white", font=("Segoe UI", 11, "bold"))

title = tk.Label(root, text="Kontrol Lampu Kamar Fathan", font=("Segoe UI", 14, "bold"),
                 fg="white", bg="#2b2b2b")
title.pack(pady=10)

# Jalankan discovery
found = discover_lamps()

for mac, nama in TARGET_MACS.items():
    ip = found.get(mac, "Tidak Ditemukan")

    frame = ttk.LabelFrame(root, text=f"{nama}   {ip}")
    frame.pack(fill="x", padx=12, pady=8, ipady=4)

    status_label = tk.Label(frame, text="...", font=("Segoe UI", 9, "bold"), bg="#3c3f41", fg="white")
    status_label.pack(pady=4)

    if ip != "Tidak Ditemukan":
        btn_frame = tk.Frame(frame, bg="#3c3f41")
        btn_frame.pack(pady=4)
        ttk.Button(btn_frame, text="ON", width=8,
                   command=lambda ip=ip, sl=status_label: lamp_on(ip, sl)).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="OFF", width=8,
                   command=lambda ip=ip, sl=status_label: lamp_off(ip, sl)).grid(row=0, column=1, padx=4)

        ttk.Label(frame, text="Brightness").pack(pady=(8, 0))
        bright_slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal",
                                  command=lambda val, ip=ip: lamp_brightness(ip, val))
        bright_slider.pack(fill="x", padx=12, pady=4)

        ttk.Label(frame, text="Color Temperature (Kelvin)").pack(pady=(8, 0))
        preview = tk.Frame(frame, height=20, bg="#ffffff")
        preview.pack(fill="x", padx=12, pady=4)

        kelvin_slider = ttk.Scale(frame, from_=2000, to=6500, orient="horizontal",
                                  command=lambda val, ip=ip, pv=preview: [lamp_kelvin(ip, val),
                                                                          pv.configure(bg=kelvin_to_hex(int(float(val))))])
        kelvin_slider.pack(fill="x", padx=12, pady=4)

        ttk.Label(frame, text="Color Hue (RGB)").pack(pady=(8, 0))
        hue_slider = HueSlider(frame, ip, height=25, bg="#3c3f41", highlightthickness=0)
        hue_slider.pack(fill="x", expand=True, padx=12, pady=4)

        root.after(500, lambda ip=ip, bs=bright_slider, ks=kelvin_slider, pv=preview,
                   sl=status_label, hs=hue_slider: sync_ui(ip, bs, ks, pv, sl, hs))

root.update()
root.minsize(root.winfo_width() + 30, root.winfo_height() + 30)
root.mainloop()

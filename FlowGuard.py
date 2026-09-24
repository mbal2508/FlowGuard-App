# -------------------------------------------------------------
# FlowGuard; Worktime and Hydration Reminder For Desktop
# Copyright (c) 2026 Jembar Muhammad Firdiana
# Licensed under the MIT License. See LICENSE file for details.
# -------------------------------------------------------------

from tkinter import *
import pyautogui
import time
from datetime import datetime, timedelta
from tkinter import messagebox
import threading
import os
import sys
import platform

def resource_path(relative_path):
    """ Ensure asset file paths work during compilation or development """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==================== MAIN UI SETTINGS ====================
window = Tk()

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

window.title("FlowGuard")
window.geometry("550x700") 
window.config(background="#1e1e2e") 

BG_APP = "#1e1e2e"
BG_FRAME = "#313244"
FG_TEXT = "#cdd6f4"
BTN_BLUE = "#89b4fa"
BTN_GREEN = "#a6e3a1"
BTN_RED = "#f38ba8"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 11)

try:
    logo = PhotoImage(file=resource_path("FlowGuard Logo's.png"))
    logo = logo.subsample(2, 2) 
    window.iconphoto(True, logo)
    has_logo = True
except:
    has_logo = False

# ==================== HELPER FUNCTIONS ====================

def safe_ui_update(widget, **kwargs):
    """ Memastikan update UI Tkinter dari Thread berjalan aman """
    window.after(0, lambda: widget.config(**kwargs))

def shutdown_computer():
    system_os = platform.system()
    if system_os == "Windows":
        os.system("shutdown /s /t 1")
    elif system_os == "Darwin": 
        os.system("osascript -e 'tell app \"System Events\" to shut down'")
    elif system_os == "Linux":
        os.system("shutdown -h now")

# ==================== PROGRAM LOGIC ====================

def process(mode, work_duration_seconds, break_duration_seconds, break_text):
    work_hour = 1
    
    while True:
        # 1. Pengecekan Waktu & Work Delay
        now = datetime.now()
        info_text = f"===== Information =====\nThis is work hour #{work_hour}\nStarted at {now.hour:02d}:{now.minute:02d}\n====================="
        safe_ui_update(label_status, text=info_text)

        if 0 <= now.hour < 5:
            ask_sleep = pyautogui.confirm(text="It's past 00:00, time to sleep.\nShutdown?", title="System", buttons=['OK', 'No'])
            if ask_sleep == "OK":
                shutdown_computer()
                
        time.sleep(work_duration_seconds)
        
        # Menggunakan pyautogui.alert karena lebih aman dipanggil dari thread dibanding messagebox Tkinter
        if work_duration_seconds >= 3600:
            pyautogui.alert(text="One hour has passed...", title="FlowGuard")
        else:
            pyautogui.alert(text="Custom work time has passed...", title="FlowGuard")

        # 2. Pengingat Hidrasi (Telah diperbaiki agar tidak infinite spam)
        while True:
            ask_water = pyautogui.confirm(text="Have you drank water?", title="Hydration Reminder", buttons=['Yes', 'Not yet'])
            if ask_water == "Yes":
                safe_ui_update(label_sys, text=" SYSTEM : Good, you are now hydrated.", fg=BTN_GREEN)
                break
            else:
                pyautogui.alert(text="Okay, I will wait 5 minutes before reminding you again.", title="FlowGuard")
                time.sleep(300) # Menunggu 5 menit sebelum bertanya lagi
                
        # 3. Waktu Istirahat
        if break_duration_seconds > 0:
            pyautogui.alert(text=f"Time to take a break for {break_text}..", title="FlowGuard")
            safe_ui_update(label_sys, text=f" SYSTEM : Time to rest for {break_text}..", fg="#f9e2af")
            time.sleep(1)

            future_time = datetime.now() + timedelta(seconds=break_duration_seconds)
            safe_ui_update(label_back_to_work, text=f" SYSTEM : Back to work at {future_time.hour:02d}:{future_time.minute:02d}")
            
            time.sleep(break_duration_seconds)
            
            pyautogui.alert(text="Break time is over, let's get back to work boss!", title="FlowGuard")
            safe_ui_update(label_back_to_work, text="")
        
        safe_ui_update(label_sys, text=" SYSTEM : Back to work boss!", fg=BTN_GREEN)
        work_hour += 1
        time.sleep(1)

def run_program(mode):
    work_duration_seconds = 3600 
    break_duration_seconds = 0
    break_text = ""
    
    if mode == "with_break":
        break_duration_seconds = 1800 
        break_text = "30 minutes"
        
    elif mode == "no_break":
        break_duration_seconds = 0
        break_text = "0 minutes"
        
    elif mode == "custom":
        val_hour = custom_hour_entry.get().strip()
        val_break = custom_break_entry.get().strip()
        
        if not val_hour: val_hour = "0"
        if not val_break: val_break = "0"
        
        # Validasi menggunakan Float agar mendukung desimal (contoh: 1.5 jam)
        try:
            hour_float = float(val_hour)
            break_float = float(val_break)
        except ValueError:
            messagebox.showerror("Input Error", "Hour and Break fields must be filled with numbers (e.g., 1 or 1.5)!")
            return 
            
        if hour_float <= 0:
            messagebox.showerror("Input Error", "Work hours must be greater than 0!")
            return 
            
        work_duration_seconds = int(hour_float * 3600)
        break_duration_seconds = int(break_float * 3600)
        break_text = f"{break_float} hours" if break_float >= 1 else f"{int(break_float * 60)} minutes"

    # Mengunci UI
    btn_preset_1.config(state="disabled", bg="#585b70")
    btn_preset_2.config(state="disabled", bg="#585b70")
    btn_custom.config(state="disabled", bg="#585b70")
    custom_hour_entry.config(state="disabled")
    custom_break_entry.config(state="disabled")
    
    # Menjalankan logika di background agar UI tidak freeze
    threading.Thread(
        target=process, 
        args=(mode, work_duration_seconds, break_duration_seconds, break_text), 
        daemon=True
    ).start()

# ==================== UI FRAME DIVISIONS ====================

frame_header = Frame(window, bg=BG_APP)
frame_header.pack(fill="x", pady=20)

if has_logo:
    label_title = Label(frame_header, text="FlowGuard", font=FONT_TITLE, fg=FG_TEXT, bg=BG_APP, image=logo, compound="left", padx=10)
else:
    label_title = Label(frame_header, text="FlowGuard", font=FONT_TITLE, fg=FG_TEXT, bg=BG_APP)
label_title.pack()

frame_preset = LabelFrame(window, text=" Quick Mode ", font=FONT_SUBTITLE, bg=BG_APP, fg=FG_TEXT, bd=1, padx=15, pady=15)
frame_preset.pack(fill="x", padx=30, pady=10)

btn_preset_1 = Button(frame_preset, text="1 Hr Work, 30 Min Break", font=FONT_NORMAL, bg=BTN_BLUE, fg="#11111b", relief="flat", cursor="hand2", command=lambda: run_program("with_break"))
btn_preset_1.pack(side="left", expand=True, fill="x", padx=5)

btn_preset_2 = Button(frame_preset, text="Work Without Break", font=FONT_NORMAL, bg=BTN_RED, fg="#11111b", relief="flat", cursor="hand2", command=lambda: run_program("no_break"))
btn_preset_2.pack(side="right", expand=True, fill="x", padx=5)

frame_custom = LabelFrame(window, text=" Custom Mode ", font=FONT_SUBTITLE, bg=BG_APP, fg=FG_TEXT, bd=1, padx=15, pady=15)
frame_custom.pack(fill="x", padx=30, pady=10)

Label(frame_custom, text="Work Hours:", font=FONT_NORMAL, bg=BG_APP, fg=FG_TEXT).grid(row=0, column=0, sticky="w", pady=5)
custom_hour_entry = Entry(frame_custom, font=FONT_NORMAL, bg=BG_FRAME, fg=FG_TEXT, relief="flat", insertbackground=FG_TEXT, width=15)
custom_hour_entry.grid(row=0, column=1, padx=10, pady=5)

Label(frame_custom, text="Break Duration\n(in hours):", font=("Segoe UI", 10, "bold"), bg=BG_APP, fg=FG_TEXT, justify="left").grid(row=1, column=0, sticky="w", pady=5)
custom_break_entry = Entry(frame_custom, font=FONT_NORMAL, bg=BG_FRAME, fg=FG_TEXT, relief="flat", insertbackground=FG_TEXT, width=15)
custom_break_entry.grid(row=1, column=1, padx=10, pady=5)

btn_custom = Button(frame_custom, text="Start Custom Mode", font=FONT_NORMAL, bg=BTN_GREEN, fg="#11111b", relief="flat", cursor="hand2", command=lambda: run_program("custom"))
btn_custom.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=15, pady=5)

frame_status = Frame(window, bg=BG_FRAME, bd=0)
frame_status.pack(fill="both", expand=True, padx=30, pady=20)

label_status = Label(frame_status, text="Program status will appear here...", font=FONT_NORMAL, bg=BG_FRAME, fg="#a6adc8", justify="center")
label_status.pack(pady=10)

label_sys = Label(frame_status, text="", font=("Courier New", 11, "bold"), bg=BG_FRAME, fg=BTN_GREEN, justify="left", anchor="w")
label_sys.pack(fill="x", padx=15, pady=2)

label_back_to_work = Label(frame_status, text="", font=("Courier New", 11, "bold"), bg=BG_FRAME, fg="#f9e2af", justify="left", anchor="w")
label_back_to_work.pack(fill="x", padx=15, pady=2)

# ==================== UI: COPYRIGHT (FOOTER) ====================
frame_footer = Frame(window, bg=BG_APP)
frame_footer.pack(fill="x", side="bottom", pady=10)

label_copyright = Label(
    frame_footer, 
    text="© 2026 Jembar Muhammad Firdiana. Licensed under the MIT License.", 
    font=("Segoe UI", 9, "italic"), 
    fg="#585b70", 
    bg=BG_APP
)
label_copyright.pack()

window.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import logging

# إعداد السجل
logging.basicConfig(level=logging.INFO)

download_thread = None
stop_download = False

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_path.set(folder_selected)

def on_progress(progress_var):
    def callback(d):
        if d['status'] == 'downloading':
            progress_str = d['_percent_str'].strip()
            # إزالة رموز ANSI الملونة
            progress_str = progress_str.replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip('%')
            try:
                percentage_of_completion = float(progress_str)
                progress_var.set(percentage_of_completion)
                log_text.insert(tk.END, f"Progress: {percentage_of_completion}%\n")
                log_text.see(tk.END)
            except ValueError:
                pass
    return callback

def start_video_download():
    global download_thread, stop_download
    url = url_entry.get()
    path = download_path.get()
    progress_var.set(0)
    log_text.insert(tk.END, "Starting video download...\n")
    disable_buttons()
    stop_download = False
    download_thread = threading.Thread(target=download_video, args=(url, path, progress_var))
    download_thread.start()

def start_playlist_download():
    global download_thread, stop_download
    url = url_entry.get()
    path = download_path.get()
    progress_var.set(0)
    log_text.insert(tk.END, "Starting playlist download...\n")
    disable_buttons()
    stop_download = False
    download_thread = threading.Thread(target=download_playlist, args=(url, path, progress_var))
    download_thread.start()

def stop_download_handler():
    global stop_download
    stop_download = True
    enable_buttons()
    log_text.insert(tk.END, "Download stopped.\n")

def download_video(url, download_path, progress_var):
    global stop_download
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=?1080]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [on_progress(progress_var)],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        if not stop_download:
            messagebox.showinfo("نجاح", "تم تنزيل الفيديو بنجاح")
            log_text.insert(tk.END, "Video downloaded successfully.\n")
    except Exception as e:
        if not stop_download:
            messagebox.showerror("خطأ", str(e))
            log_text.insert(tk.END, f"Error: {str(e)}\n")
    finally:
        enable_buttons()

def download_playlist(url, download_path, progress_var):
    global stop_download
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=?1080]+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{download_path}/%(playlist)s/%(title)s.%(ext)s',
            'progress_hooks': [on_progress(progress_var)],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            total_videos = len(info_dict['entries'])
            for i, entry in enumerate(info_dict['entries']):
                if stop_download:
                    break
                video_url = entry['webpage_url']
                progress_var.set((i + 1) / total_videos * 100)
                ydl.download([video_url])
                log_text.insert(tk.END, f"Downloaded video {i + 1}/{total_videos}\n")
                log_text.see(tk.END)
        if not stop_download:
            messagebox.showinfo("نجاح", "تم تنزيل جميع الفيديوهات بنجاح")
            log_text.insert(tk.END, "All videos downloaded successfully.\n")
    except Exception as e:
        if not stop_download:
            messagebox.showerror("خطأ", str(e))
            log_text.insert(tk.END, f"Error: {str(e)}\n")
    finally:
        enable_buttons()

def disable_buttons():
    download_button.config(state=tk.DISABLED)
    playlist_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    path_button.config(state=tk.DISABLED)

def enable_buttons():
    download_button.config(state=tk.NORMAL)
    playlist_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    path_button.config(state=tk.NORMAL)

# إعداد واجهة المستخدم
root = tk.Tk()
root.title("برنامج تحميل الفيديوهات من YouTube")
root.geometry("600x400")
root.resizable(False, False)

# الألوان المستخدمة
colors = ["#ff8a8a", "#fff48a", "#e0ffd8", "#8affff"]

# نمط ttk مع ألوان مخصصة
style = ttk.Style(root)
style.theme_use('clam')
style.configure("TLabel", font=("Arial", 12), background=colors[0], foreground="black")
style.configure("TButton", font=("Arial", 12), background=colors[1], foreground="black", borderwidth=2, relief="groove")
style.map("TButton", background=[('active', colors[2])])
style.configure("TEntry", font=("Arial", 12), fieldbackground=colors[3], foreground="black")
style.configure("TFrame", background=colors[0])
style.configure("TLabelFrame", background=colors[0], foreground="black")
style.configure("TProgressbar", troughcolor=colors[1], background=colors[2])

# إدخال الرابط
url_label = ttk.Label(root, text="ضع رابط الفيديو أو قائمة التشغيل:")
url_label.pack(pady=10)
url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=10)

# زر تحديد موقع التحميل
download_path = tk.StringVar()
path_button = ttk.Button(root, text="اختر موقع التحميل", command=browse_folder)
path_button.pack(pady=10)
path_label = ttk.Label(root, textvariable=download_path)
path_label.pack(pady=5)

# أزرار التحميل
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

download_button = ttk.Button(button_frame, text="تحميل فيديو", command=start_video_download)
download_button.pack(side=tk.LEFT, padx=5)

playlist_button = ttk.Button(button_frame, text="تحميل بلاي ليست", command=start_playlist_download)
playlist_button.pack(side=tk.LEFT, padx=5)

stop_button = ttk.Button(button_frame, text="إيقاف التحميل", command=stop_download_handler)
stop_button.pack(side=tk.LEFT, padx=5)
stop_button.config(state=tk.DISABLED)

# شريط التقدم
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, padx=10, fill=tk.X)

# مساحة عرض رسائل السجل
log_frame = ttk.LabelFrame(root, text="السجل")
log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, bg=colors[3], fg="black")
log_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

# ضبط خلفية البرنامج
root.configure(bg=colors[0])

# بدء واجهة المستخدم
root.mainloop()

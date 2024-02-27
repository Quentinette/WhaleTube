import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import os
import sys
import importlib.util
from pytube import YouTube
from pytube import Playlist
from ttkthemes import ThemedTk
from PIL import Image, ImageTk

if getattr(sys, 'frozen', False):
    import pyi_splash

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur Youtube de Quentin")

        print("Checking and installing packages...")
        self.check_and_install_packages()

        window_width = 560
        window_height = 130
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'icon.ico')

        root.iconbitmap(default=icon_path)

        self.video_link = tk.StringVar()
        self.download_type = tk.StringVar()
        self.download_state = tk.StringVar()
        self.download_state.set("")

        self.download_path = os.path.join(os.path.join(os.path.expanduser('~'), 'Desktop'), 'Téléchargement Youtube')
        self.audio_path = os.path.join(self.download_path, 'Audio')
        self.video_path = os.path.join(self.download_path, 'Video')

        self.create_widgets()

    def create_widgets(self):
        self.root.set_theme("equilux")
        self.root.configure(bg='#1e1e1e') 

        link_label = ttk.Label(self.root, text="Lien Youtube:", background='#1e1e1e', foreground='white')
        link_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.link_entry = ttk.Entry(self.root, textvariable=self.video_link, width=50)
        self.link_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.link_entry.insert(0, "Coller le lien YouTube ici")
        self.link_entry.bind("<FocusIn>", self.on_entry_click)
        self.link_entry.bind("<FocusOut>", self.on_focus_out)

       
        paste_button = ttk.Button(self.root, text="Coller", command=self.paste_from_clipboard)
        paste_button.grid(row=0, column=2, padx=5, pady=10)

        download_type_label = ttk.Label(self.root, text="Type de fichier:", background='#1e1e1e', foreground='white')
        download_type_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.download_type.set("Video")
        download_type_menu = ttk.OptionMenu(self.root, self.download_type, "Video", "Video", "Audio")
        download_type_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        download_button = ttk.Button(self.root, text="Télécharger", command=self.download_media)
        download_button.grid(row=1, column=2, padx=10, pady=10, sticky="e")

        self.download_state_label = ttk.Label(self.root, textvariable=self.download_state, background='#1e1e1e', foreground='white')
        self.download_state_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.version_label = ttk.Label(self.root, text="v1.03  Maho.Lab CC", background='#1e1e1e', foreground='white')
        self.version_label.grid(row=2, column=2, columnspan=3, padx=0, pady=10, sticky="ew")

    def on_entry_click(self, event):
        if self.link_entry.get() == "Coller le lien YouTube ici":
            self.link_entry.delete(0, "end")
            self.link_entry.insert(0, '') 
            self.link_entry.config(fg = 'black')

    def on_focus_out(self, event):
        if self.link_entry.get() == '':
            self.link_entry.insert(0, 'Coller le lien YouTube ici')
            self.link_entry.config(fg = 'grey')

    def paste_from_clipboard(self):
        clipboard_content = self.root.clipboard_get()
        if clipboard_content.startswith("https://youtu.be/") or clipboard_content.startswith("https://www.youtube.com/"):
            self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, clipboard_content)
            self.download_state.set("")
        else:
        
            self.download_state.set("Le contenu du presse-papiers n'est pas un lien YouTube valide.")


    def check_and_install_packages(self):
        required_packages = ['tkinter', 'pytube', 'ttkthemes']

        missing_packages = {
            'tkinter': 'python-tk', 
            'pytube': 'pytube',
            'ttkthemes': 'ttkthemes'
        }

        def check_package(package):
            spec = importlib.util.find_spec(package)
            return spec is not None

        def install_package(package):
            install_command = f"pip install {missing_packages[package]}"
            os.system(install_command)

        for package in required_packages:
            if not check_package(package):
                self.download_state.set(f"Le package {package} est manquant. Installation en cours...")
                install_package(package)
                
                if not check_package(package):
                    self.download_state.set(f"Impossible d'installer le package {package}. Veuillez l'installer manuellement.")
                    sys.exit(1)

        print("Toutes les bibliothèques nécessaires sont installées. Le programme peut être exécuté.")

    def download_media(self):
        video_link = self.video_link.get()
        download_type = self.download_type.get()

        def download():
            self.download_state.set("Téléchargement en cours...")
            if video_link.startswith("https://www.youtube.com/playlist"):
                self.download_playlist(video_link, download_type)
                stream.download(output_path=destination_path, filename=filename)
                self.download_state.set("Téléchargement terminé")
                self.link_entry.delete(0, 'end')
            else:
                yt = YouTube(video_link)
                if download_type == "Video":
                    stream = yt.streams.get_highest_resolution()
                    filename = yt.title + '.mp4'  
                    destination_path = self.video_path
                elif download_type == "Audio":
                    stream = yt.streams.filter(only_audio=True).get_audio_only(subtype='mp4')
                    filename = yt.title + '.mp3'
                    destination_path = self.audio_path

                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)

                stream.download(output_path=destination_path, filename=filename)
                self.download_state.set("Téléchargement terminé")
                self.link_entry.delete(0, 'end') 

        download_thread = threading.Thread(target=download)
        download_thread.start()



if getattr(sys, 'frozen', False):
    pyi_splash.close()

root = ThemedTk(theme="equilux")
app = YouTubeDownloaderApp(root)
root.mainloop()

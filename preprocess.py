import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
import sounddevice as sd
import numpy as np
import librosa
import librosa.display
from itertools import cycle

# Configure visualization style
sns.set_theme(style="white", palette=None)
color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])

# Global variables
figures = []
current_graph_index = 0
y = None
fs = 44100  # Sample rate


def start_record_sound(status_label, frame_plot, button_next):
    global y, fs, current_graph_index, figures
    current_graph_index = 0
    figures = []
    button_next.config(state=tk.NORMAL)

    seconds = 5  # Duration of recording

    status_label.config(text="Recording...", foreground="#F77D2E")
    status_label.update()

    # Record the audio
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait() 
    y = myrecording[:, 0]

    status_label.config(text="Processing audio...")
    status_label.update()

    process_audio(frame_plot)
    status_label.config(text="Finished")

def process_audio(frame_plot):
    global figures, y, fs

    # Plot the raw audio
    fig1 = plt.figure(figsize=(10, 5))
    plt.plot(y, lw=1, label='Raw Audio', color=next(color_cycle))
    plt.title('Raw Audio Example')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.tight_layout()
    figures.append(fig1)

    # Trimming leading/lagging silence
    y_trimmed, _ = librosa.effects.trim(y, top_db=20)

    # Plot the trimmed audio
    fig2 = plt.figure(figsize=(10, 5))
    plt.plot(y_trimmed, lw=1, label='Trimmed Audio', color=next(color_cycle))
    plt.title('Trimmed Audio Example')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.tight_layout()
    figures.append(fig2)

     # Zoom in on a section of the audio
    fig3 = plt.figure(figsize=(10, 5))
    plt.plot(y[30000:30500], lw=1, label='Zoomed Audio', color=next(color_cycle))
    plt.title('Zoomed In Audio Example')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.tight_layout()
    figures.append(fig3)

    # Calculate the spectrogram
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    # Plot the spectrogram
    fig4 = plt.figure(figsize=(10, 5))
    img = librosa.display.specshow(S_db, x_axis='time', y_axis='log')
    plt.title('Spectrogram Example')
    plt.colorbar(img, format='%0.2f')
    plt.tight_layout() 
    figures.append(fig4)

    # Calculate the mel spectrogram
    S = librosa.feature.melspectrogram(y=y, sr=fs, n_mels=128 * 2)
    S_db_mel = librosa.amplitude_to_db(S, ref=np.max)

    # Plot the mel spectrogram
    fig5 = plt.figure(figsize=(10, 5))
    img = librosa.display.specshow(S_db_mel, x_axis='time', y_axis='log')
    plt.title('Mel Spectrogram Example')
    plt.colorbar(img, format='%0.2f')
    plt.tight_layout()
    figures.append(fig5)

    display_graph(frame_plot)

def display_graph(frame_plot):
    global current_graph_index

    for widget in frame_plot.winfo_children():
        widget.destroy()

    if current_graph_index < len(figures):
        canvas = FigureCanvasTkAgg(figures[current_graph_index], master=frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack()

def next_graph(status_label, frame_plot, button_next):
    global current_graph_index

    current_graph_index += 1
    if current_graph_index < len(figures):
        display_graph(frame_plot)
    else:
        status_label.config(text="Finished")
        button_next.config(state=tk.DISABLED)

def create_preprocessing_tab(parent):

    parent.configure(bg="#E2F1E7")

    style = ttk.Style()
    style.configure("Custom.TFrame", background="#E2F1E7")

    # Title Label
    title_logo = tk.PhotoImage(file="misc\\soundprep.png")
    label_title = ttk.Label(parent, text="Sound Preprocessing", font=("Segoe UI", 24, "bold"),
                            foreground="#243642", background="#E2F1E7",image= title_logo,compound = 'right' )
    label_title.image = title_logo
    label_title.pack(pady=20)

    # Status Label
    status_label = ttk.Label(parent, text="", font=("Segoe UI", 12),foreground="#F86506", background="#E2F1E7")
    status_label.pack(pady=5)

    # Plot Frame
    frame_plot = ttk.Frame(parent, style="Custom.TFrame")
    frame_plot.pack(pady=10, padx=10, side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Button Frame
    button_frame = ttk.Frame(parent, style="Custom.TFrame") 
    button_frame.pack(pady=10, side=tk.RIGHT)

    # Record Button
    button_record = tk.Button(
        button_frame, 
        text="Start Recording", 
        font=("Segoe UI", 12), 
        fg="#000000", 
        bg="#0a75ad",
        command=lambda: start_record_sound(status_label, frame_plot, button_next),
        activebackground="#05a2f5",
        activeforeground="#000000"
    )
    button_record.pack(pady=10)

    # Next Button
    button_next = tk.Button(
        button_frame, 
        text="Next", 
        font=("Segoe UI", 12), 
        fg="#000000", 
        bg="#ff4040",
        state=tk.DISABLED, 
        command=lambda: next_graph(status_label, frame_plot, button_next),
        activebackground="#ff0000",
        activeforeground="#000000"
    )
    button_next.pack(pady=10)

import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
import speech_recognition as sr
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import threading
from sklearn.metrics import accuracy_score, f1_score
from sentiment import create_tab2
from preprocess import create_preprocessing_tab
from analyze import create_topic_tab
from identify import create_identify_tab

class SpeechAnalyzerApp:

    def __init__(self, root):
        self.recognizer = sr.Recognizer()
        self.stop_recording = False
        self.graph_button_pressed = False
        self.root = root
        self.root.title("Speech Recognition and Analysis")
        self.root.geometry("800x600")
        self.root.configure(bg='#E2F1E7') 
        icon = tk.PhotoImage(file='misc\\icon.png')
        self.root.iconphoto(True, icon)

        # Side menu frame
        self.side_menu = tk.Frame(self.root, bg='#9aa49d', width=100)
        self.side_menu.pack(side='left', fill='y')

        # Buttons for side menu
        tab1_button = tk.Button(self.side_menu, text="Preprocess", font=("Segoe UI", 12, 'bold'), bg='#243642', fg='#ffffff', command=self.show_preprocess_tab)
        tab1_button.pack(fill='x', pady=15, padx=5)

        tab2_button = tk.Button(self.side_menu, text="Record", font=("Segoe UI", 12, 'bold'), bg='#243642', fg='#ffffff', command=self.show_record_tab)
        tab2_button.pack(fill='x', pady=15, padx=5)

        tab3_button = tk.Button(self.side_menu, text="Identify", font=("Segoe UI", 12, 'bold'), bg='#243642', fg='#ffffff', command=self.show_identify_tab)
        tab3_button.pack(fill='x', pady=15, padx=5)

        tab4_button = tk.Button(self.side_menu, text="Analyze", font=("Segoe UI", 12, 'bold'), bg="#243642", fg="#ffffff", command=self.show_analyze_tab)
        tab4_button.pack(fill="x", pady=15, padx=5)

        tab5_button = tk.Button(self.side_menu, text="Summary", font=("Segoe UI", 12, 'bold'), bg="#243642", fg="#ffffff", command=self.show_topic_tab)
        tab5_button.pack(fill="x", pady=15, padx=5)

        # User management
        self.users = []
        self.current_user = tk.StringVar(value="")
        self.add_user_management_ui()
        self.load_users()

        # Main content frame
        self.main_frame = tk.Frame(self.root, bg='#E2F1E7')
        self.main_frame.pack(side='right', fill='both', expand=True)

        # Initialize tabs
        self.record_tab = tk.Frame(self.main_frame, bg='#E2F1E7')
        self.analyze_tab = tk.Frame(self.main_frame, bg='#E2F1E7')
        self.preprocess_tab = tk.Frame(self.main_frame, bg='#E2F1E7')
        self.topic_tab = tk.Frame(self.main_frame, bg="#E2F1E7")
        self.identify_tab = tk.Frame(self.main_frame, bg="#E2F1E7")
        self.setup_ui(self.record_tab)
        self.show_identify_tab()

    # User management
    def add_user_management_ui(self):
        user_frame = tk.Frame(self.side_menu, bg='#9aa49d')
        user_label = tk.Label(self.side_menu, text="All users:", font=("Segoe UI", 14, "bold"), bg='#9aa49d', fg='#000000')
        user_label.pack(side='top', pady=20, padx=5)
        style = ttk.Style()
        style.configure('TCombobox', fieldbackground='lightblue', background='white', arrowcolor='black', selectbackground='grey', selectforeground='white')
        self.user_dropdown = ttk.Combobox(user_frame, textvariable=self.current_user, state="readonly", font=("Segoe UI", 12,), style='TCombobox', width=10)
        self.user_dropdown.pack(side='bottom')
        user_frame.pack(side='top', fill='x', padx=5)
        tab6_button = tk.Button(self.side_menu, text="Add User", font=("Segoe UI", 10, 'bold'), bg="#243642", fg="#ffffff", command=self.add_user)
        tab6_button.pack(fill="x", pady=15, padx=5)
        tab6_button = tk.Button(self.side_menu, text="Delete User", font=("Segoe UI", 10, 'bold'), bg="#243642", fg="#ffffff", command=self.delete_user)
        tab6_button.pack(fill="x", padx=5)
        
    def add_user(self):
        user_name = tk.simpledialog.askstring("Add user", "Enter user name:")
        if user_name and user_name not in self.users:
            self.users.append(user_name)
            self.save_users()
            self.update_user_dropdown()

    def delete_user(self):

        messagebox.showwarning("Warning", "This will delete all data associated with the user. Are you sure you want to delete the user?")
        user_name = self.current_user.get()
        if user_name in self.users:
            self.users.remove(user_name)
            self.save_users()
            self.update_user_dropdown()
            
            # Delete associated files
            try:
                audio_folder = "saved_audio"
                text_folder = "saved_texts"
                npy_folder = "model/mfcc"
                
                if os.path.exists(audio_folder):
                    for file in os.listdir(audio_folder):
                        if file.startswith(user_name):
                            os.remove(os.path.join(audio_folder, file))
                
                if os.path.exists(text_folder):
                    for file in os.listdir(text_folder):
                        if file.startswith(user_name):
                            os.remove(os.path.join(text_folder, file))
                
                if os.path.exists(npy_folder):
                    for file in os.listdir(npy_folder):
                        if file.startswith(user_name):
                            os.remove(os.path.join(npy_folder, file))
                
                messagebox.showinfo("Success", f"All data for user '{user_name}' has been deleted.")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting files for user '{user_name}': {e}")
            
            if self.users:
                self.current_user.set(self.users[0])
            else:
                self.current_user.set("")

    def update_user_dropdown(self):
        self.user_dropdown['values'] = self.users

    def load_users(self):
    
        try:
            if os.path.exists("misc/users.txt"):
                with open("misc/users.txt", "r") as file:
                    self.users = [line.strip() for line in file.readlines()]
                if self.users:
                    self.current_user.set(self.users[0])
            self.update_user_dropdown()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load users: {e}")

    def save_users(self):
        try:
            with open("misc/users.txt", "w") as file:
                for user in self.users:
                    file.write(user + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save users: {e}")

    # Tabs
    def show_record_tab(self):
        self.analyze_tab.pack_forget()
        self.preprocess_tab.pack_forget()
        self.topic_tab.pack_forget()
        self.identify_tab.pack_forget()
        self.record_tab.pack(fill="both", expand=True)

    def show_analyze_tab(self):
        self.record_tab.pack_forget()
        self.preprocess_tab.pack_forget()
        self.topic_tab.pack_forget()
        self.identify_tab.pack_forget()
        if not hasattr(self, "sentiment_initialized"):
            create_tab2(self.analyze_tab)
            self.sentiment_initialized = True
        self.analyze_tab.pack(fill="both", expand=True)

    def show_preprocess_tab(self):
        self.record_tab.pack_forget()
        self.analyze_tab.pack_forget()
        self.topic_tab.pack_forget()
        self.identify_tab.pack_forget()
        if not hasattr(self, "preprocess_initialized"):
            create_preprocessing_tab(self.preprocess_tab)
            self.preprocess_initialized = True
        self.preprocess_tab.pack(fill="both", expand=True)

    def show_topic_tab(self):
        self.record_tab.pack_forget()
        self.analyze_tab.pack_forget()
        self.preprocess_tab.pack_forget()
        self.identify_tab.pack_forget()
        if not hasattr(self, "topic_initialized"):
            create_topic_tab(self.topic_tab)
            self.topic_initialized = True
        self.topic_tab.pack(fill="both", expand=True)

    def show_identify_tab(self):
        self.record_tab.pack_forget()
        self.analyze_tab.pack_forget()
        self.preprocess_tab.pack_forget()
        self.topic_tab.pack_forget()
        if not hasattr(self, "identify_initialized"):
            create_identify_tab(self.identify_tab)
            self.identify_initialized = True
        self.identify_tab.pack(fill="both", expand=True)

    # Main Record Tab UI
    def setup_ui(self, parent):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#E2F1E7', foreground='#243642', font=("Segoe UI", 14))
        style.configure('Custom.TEntry', fieldbackground='#FFFFFF', foreground='#000000')
        style.configure('TFrame', background='#E2F1E7')

        # Title label
        self.titleLogo = tk.PhotoImage(file='misc\\titleLogo.png')
        title_label = ttk.Label(parent, text="Record Your Audio", font=("Segoe UI", 24, "bold"),
                        background='#E2F1E7', foreground='#243642', image=self.titleLogo, compound='right')
        title_label.pack(pady=15)

        # Status label
        self.statusIcon01 = tk.PhotoImage(file='misc\\info.png')
        self.status_label = ttk.Label(parent, text="Ready", font=("Segoe UI", 10, 'bold'), background="#E2F1E7", foreground="#00441B")
        self.status_label.config(image=self.statusIcon01)
        self.status_label.config(compound='left')
        self.status_label.pack(pady=5)

        # Word count label
        self.word_count_label = ttk.Label(parent, text="")
        self.word_count_label.pack(pady=3)

        # Recognized text label
        ttk.Label(parent, text="Recognized Text:", font=("Segoe UI", 12, 'bold')).pack(pady=3)

        # Text entry for displaying recognized text
        self.result_var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=self.result_var, font=("Segoe UI", 10), width=60, style='Custom.TEntry')
        entry.pack(pady=3)

        # Buttons
        button_frame = ttk.Frame(parent, style='TFrame')
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Start", command=self.start_recording, font=("Segoe UI", 15),
                bg="#4caf50", fg="#000000", activebackground="#388e3c", activeforeground="#000000").grid(row=0, column=0, padx=5)

        tk.Button(button_frame, text="Stop", command=self.stop_recording_action, font=("Segoe UI", 15),
                bg="#ff4040", fg="#000000", activebackground="#ff0000", activeforeground="#000000").grid(row=0, column=1, padx=5)

        tk.Button(button_frame, text="Clear", command=self.clear_ui, font=("Segoe UI", 15),
                bg="#617e8c", fg="#000000", activebackground="#243642", activeforeground="#000000").grid(row=0, column=2, padx=5)

        tk.Button(button_frame, text="Save", command=self.autoSaveFile, font=("Segoe UI", 15),
                bg="#ffde21", fg="#000000", activebackground="#ffd900", activeforeground="#000000").grid(row=0, column=3, padx=5)
        
        tk.Button(button_frame, text="Graph", command=self.show_graph, font=("Segoe UI", 15),
          bg="#0a75ad", fg="#000000", activebackground="#05a2f5", activeforeground="#000000").grid(row=0, column=4, padx=5)

        # Histogram canvas frame
        self.canvas_frame = ttk.Frame(parent)
        self.canvas_frame.pack(pady=10, padx=10)

        # Accuracy and F-measure labels
        self.acc_label = ttk.Label(parent, text="")
        self.acc_label.pack(pady=15)
        self.fm_label = ttk.Label(parent, text="")
        self.fm_label.pack(pady=15)

   
    def count_words(self, text):
        return len(text.split())
    
    def autoSaveFile(self):
        if not self.current_user.get():
            messagebox.showwarning("No User Selected", "Please select a user before saving.")
            return
        
        user_name = self.current_user.get()
        save_text = "saved_texts"
        save_audio = "saved_audio"
        os.makedirs(save_text, exist_ok=True)
        os.makedirs(save_audio, exist_ok=True)
        
        # Get next file number
        file_number = 1
        while os.path.exists(os.path.join(save_text, f"{user_name}{file_number}.txt")) or \
            os.path.exists(os.path.join(save_audio, f"{user_name}{file_number}.wav")):
            file_number += 1
        
        # Save text file
        text_filename = os.path.join(save_text, f"{user_name}{file_number}.txt")
        try:
            with open(text_filename, 'w') as f:
                filetext = self.result_var.get()
                f.write(filetext)
            self.status_label.config(text=f"Text saved: {text_filename}", foreground="#00441B")
        except Exception as e:
            self.status_label.config(text=f"Error saving text: {e}", foreground="red")
        
        # Save audio file
        audio_filename = os.path.join(save_audio, f"{user_name}{file_number}.wav")
        try:
            if self.audio_data:
                with open(audio_filename, "wb") as audio_file:
                    audio_file.write(self.audio_data.get_wav_data())
                self.status_label.config(text=f"Audio saved: {audio_filename}", foreground="#00441B")
            else:
                self.status_label.config(text="No audio recorded to save.", foreground="#f44336")
        except Exception as e:
            self.status_label.config(text=f"Error saving audio: {e}", foreground="red")

    def create_histogram(self, text):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        word_counts = Counter(text.split())

        plt.figure(figsize=(10, 6))
        sns.set_theme(style="darkgrid")
        sns.barplot(x=list(word_counts.keys()), y=list(word_counts.values()), color='blue')
        plt.xlabel('Words')
        plt.ylabel('Frequency')
        plt.title('Word Frequency Histogram', color='#000000')
        plt.xticks(rotation=45, ha='right', color='#000000')
        plt.yticks(color='#000000')
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def show_graph(self):
        final_text = self.result_var.get()
        if not final_text.strip():
            self.status_label.config(text="No words to display in graph", foreground="#f44336")
            return
        self.create_histogram(final_text)
        self.status_label.config(text="Graph displayed", foreground="#00441B")

    def clear_histogram(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

    def start_recording(self):
        self.stop_recording = False  # Reset the stop flag
        threading.Thread(target=self._record_audio, daemon=True).start()

    def _record_audio(self):
        """Record audio using the microphone."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.status_label.config(text="Listening...", foreground="#00441B")
            self.root.update_idletasks()
            full_text = ""
            self.audio_data = None  # Reset audio data before recording
            
            try:
                while not self.stop_recording:
                    # Listen for a chunk of audio
                    audio_data = self.recognizer.listen(source, timeout=None, phrase_time_limit=30)
                    self.audio_data = audio_data  # Save the most recent audio data
                    text = self.recognizer.recognize_google(audio_data, language="en-US")
                    full_text += text + " "
                    
                    # Update GUI with recognized text
                    self.root.after(0, self.update_gui, full_text)
                
                # When stopped, finalize the processing
                reference_text = "hello how are you"
                self.calculate_metrics(full_text, reference_text)
                self.status_label.config(text="Recording Stopped", foreground="#B22222")

            except sr.UnknownValueError:
                self.show_error("Could not understand the audio.")
            except sr.RequestError as e:
                self.show_error(f"System error: {e}")
            except Exception as e:
                self.show_error(str(e))

    def update_gui(self, full_text):
        self.result_var.set(full_text)
        self.word_count_label.config(text=f"Total Words: {self.count_words(full_text)}")
        if self.graph_button_pressed:
            self.create_histogram(full_text)

    def stop_recording_action(self):
        self.stop_recording = True
        self.status_label.config(text="Recording Stopped, please wait...", foreground="#B22222")

    def calculate_metrics(self, recognized_text, reference_text):
        recognized_words = recognized_text.split()
        reference_words = reference_text.split()
        if len(recognized_words) > len(reference_words):
            reference_words.extend([''] * (len(recognized_words) - len(reference_words)))
        elif len(reference_words) > len(recognized_words):
            recognized_words.extend([''] * (len(reference_words) - len(recognized_words)))
        accuracy = accuracy_score(reference_words, recognized_words)
        f_measure = f1_score(reference_words, recognized_words, average='weighted', zero_division=1)
        self.acc_label.config(text=f"Accuracy: {accuracy * 100:.2f}%")
        self.fm_label.config(text=f"F-Measure: {f_measure * 100:.2f}%")

    def show_error(self, message):
        self.status_label.config(text="Error", foreground="#f44336")
        messagebox.showerror("Error", message)
        self.clear_ui()

    def clear_ui(self):
        self.result_var.set("")
        self.status_label.config(text="Ready", font=("Segoe UI", 10, 'bold'), foreground="#00441B")
        self.word_count_label.config(text="")
        self.acc_label.config(text="")
        self.fm_label.config(text="")
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def on_graph_button_press(self):
        self.graph_button_pressed = True
        self.update_gui(self.result_var.get())

def wait_for_signal():
    signal_file = "start_main_signal.txt"
    while not os.path.exists(signal_file):
        time.sleep(0.1)
    os.remove(signal_file)

if __name__ == "__main__":
    if "wait" in os.environ:
        wait_for_signal()
    root = tk.Tk()
    app = SpeechAnalyzerApp(root)
    root.mainloop()

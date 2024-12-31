import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string
from collections import Counter
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('punkt')

def analyze_text(file_path, frame, status_label):
    status_label.config(text="Processing... Please wait", fg="orange")
    frame.update_idletasks()

    # Read and clean text
    text = open(file_path, encoding='utf-8').read()
    lower_case = text.lower()
    cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))

    # Tokenize and remove stop words
    tokenized_words = word_tokenize(cleaned_text, "english")
    final_words = [word for word in tokenized_words if word not in stopwords.words('english')]

    # Lemmatize words
    lemma_words = [WordNetLemmatizer().lemmatize(word) for word in final_words]

    # Extract emotions
    emotion_list = []
    try:
        with open('misc\\emotions.txt', 'r') as file:
            for line in file:
                clear_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
                word, emotion = clear_line.split(':')
                if word in lemma_words:
                    emotion_list.append(emotion)
    except FileNotFoundError:
        status_label.config(text="Error: emotions.txt not found", fg="red")
        return

    w = Counter(emotion_list)

    # Sentiment analysis
    score = SentimentIntensityAnalyzer().polarity_scores(cleaned_text)
    if score['neg'] > score['pos']:
        sentiment = "Negative Sentiment"
    elif score['neg'] < score['pos']:
        sentiment = "Positive Sentiment"
    else:
        sentiment = "Neutral Sentiment"

    # Plot and embed the graph in the frame
    fig, ax = plt.subplots()
    ax.bar(w.keys(), w.values(), color="blue")
    fig.autofmt_xdate()

    for widget in frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    status_label.config(text=f"Success! Sentiment: {sentiment}", fg="green")
 
def clear_graph(frame, status_label):
    for widget in frame.winfo_children():
        widget.destroy()
    status_label.config(text="", fg="black")

def on_analyze_button_click(frame, status_label):
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        analyze_text(file_path, frame, status_label)

def create_tab2(parent):

    parent.configure(bg="#E2F1E7")

    title_logo = tk.PhotoImage(file="misc\\analyze.png")
    label = tk.Label(parent, text="Sentiment Analysis", font=("Segoe UI", 24, "bold"),
                     image= title_logo, compound= 'right', fg="#243642", bg="#E2F1E7", padx=10, pady=10)
    label.image = title_logo
    label.pack(pady=20)

    button_frame = tk.Frame(parent, bg="#E2F1E7")
    button_frame.pack(pady=10)

    frame = tk.Frame(parent, width=500, height=300, bg="#E2F1E7")
    frame.pack(pady=10, padx=10)

    status_label = tk.Label(parent, text="", font=("Segoe UI", 14), fg="black", bg="#E2F1E7")
    status_label.pack(pady=10)

    analyze_button = tk.Button(
        button_frame, text="Analyze", font=("Segoe UI", 15), fg="#000000", bg="#0a75ad",
        padx=15, pady=5, activebackground="#05a2f5", activeforeground="#000000",
        command=lambda: on_analyze_button_click(frame, status_label)
    )
    analyze_button.pack(side="left", padx=10)

    clear_button = tk.Button(
        button_frame, text="Clear", font=("Segoe UI", 15), fg="#000000", bg="#ff4040",
        padx=15, pady=5, activebackground="#ff0000", activeforeground="#000000",
        command=lambda: clear_graph(frame, status_label)
    )
    clear_button.pack(side="left", padx=10)


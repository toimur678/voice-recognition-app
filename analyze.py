from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

def create_topic_tab(parent):
    parent.configure(bg="#E2F1E7")

    # Title Label
    title_logo = tk.PhotoImage(file="misc\\summary.png")
    title_label = tk.Label(parent, text="Topic Summary", font=("Segoe UI", 24, "bold"), bg="#E2F1E7", fg="#243642", image=title_logo, compound='right', padx=10, pady=10)
    title_label.image = title_logo
    title_label.pack(pady=10)

    # Buttons Frame
    button_frame = tk.Frame(parent, bg="#E2F1E7")
    button_frame.pack(pady=10)

    # Status Label
    status_label = tk.Label(parent, text="", font=("Segoe UI", 12), fg="green", bg="#E2F1E7")
    status_label.pack(pady=5)

    # Placeholder for the graph canvas
    canvas_container = tk.Frame(parent, bg="#E2F1E7")
    canvas_container.pack(pady=10, fill=tk.BOTH, expand=True)
    
    # Initialize variables to hold the figure and canvas
    figure = None
    canvas = None

    def select_file():
        nonlocal figure, canvas

        file_path = filedialog.askopenfilename(title="Select a Text File", filetypes=[("Text Files", "*.txt")])
        if not file_path:
            messagebox.showwarning("No File Selected", "Please select a valid text file.")
            return
        

        status_label.config(text="Processing... Please wait.", fg="blue")
        parent.update_idletasks()

        start_time = time.time()

        try:
            # Read the text data
            with open(file_path, 'r', encoding='utf-8') as file:
                texts = [line.strip() for line in file if line.strip()]

            if len(texts) < 2:
                messagebox.showerror("Insufficient Data", "The file must contain at least two lines of text.")
                status_label.config(text="Processing failed due to insufficient data.", fg="red")
                return

            # Configure CountVectorizer
            vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words="english")

            # Initialize BERTopic
            topic_model = BERTopic(
                vectorizer_model=vectorizer,
                min_topic_size=2  # Allow smaller topics
            )

            # Fit and transform the text data
            topics, probs = topic_model.fit_transform(texts)

            # Get the topic keywords to label each topic
            topic_info = topic_model.get_topic_info()
            topic_map = topic_info.set_index('Topic')['Name'].to_dict()

            # Filter out "Unknown" topics (-1)
            valid_indices = [i for i, topic in enumerate(topics) if topic != -1]
            filtered_topics = [topics[i] for i in valid_indices]

            # Calculate metrics
            precision, recall, f1, support = precision_recall_fscore_support(
                filtered_topics, filtered_topics, average=None
            )

            # Create a DataFrame for the metrics
            metrics = pd.DataFrame({
                'Topic': [topic_map[topic] for topic in set(filtered_topics)],
                'Precision': precision,
                'Recall': recall,
                'F1-Score': f1,
                'Support': support
            })

            # Set the Topic as the index for better plotting
            metrics.set_index('Topic', inplace=True)

            # Plotting the metrics for each topic
            fig, ax = plt.subplots(figsize=(12, 6))
            metrics.plot(kind='bar', ax=ax, width=0.8)

            # Adding titles and labels
            ax.set_title('Evaluation Metrics per Topic', fontsize=14)
            ax.set_ylabel('Score', fontsize=12)
            ax.set_xlabel('Topic', fontsize=12)

            # Rotate x-axis labels for better readability
            ax.tick_params(axis='x', labelsize=8)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_horizontalalignment('right')

            # Adjust layout for better fitting
            plt.tight_layout()

            figure = fig

            # Embed the plot in the Tkinter app
            if canvas:
                canvas.get_tk_widget().destroy()

            canvas = FigureCanvasTkAgg(figure, master=canvas_container)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10, fill=tk.BOTH, expand=True)

            status_label.config(
                text=f"Processing completed in {time.time() - start_time:.2f} seconds.", fg="green"
            )

        except Exception as e:
            status_label.config(text=f"An error occurred: {e}", fg="red")

    def clear_graph():
        nonlocal canvas

        if canvas:
            canvas.get_tk_widget().destroy()
            canvas = None
        status_label.config(text="Graph cleared.", fg="green")

    # Buttons
    select_file_button = tk.Button(
        button_frame, text="Select File", font=("Segoe UI", 14), bg="#0a75ad", fg="black", command=select_file, activebackground="#05a2f5", activeforeground="#000000"
    )
    select_file_button.grid(row=0, column=0, padx=10)

    clear_graph_button = tk.Button(
        button_frame, text="Clear Graph", font=("Segoe UI", 14), bg="#ff4040", fg="black", command=clear_graph, activebackground="#ff0000", activeforeground="#000000"
    )
    clear_graph_button.grid(row=0, column=1, padx=10)

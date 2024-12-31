import os
import tkinter as tk
from tkinter import Label, Button, messagebox
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import librosa
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import sounddevice as sd
import soundfile as sf
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import classification_report, confusion_matrix
from collections import Counter
import matplotlib.pyplot as plt

def create_identify_tab(parent):
    parent.configure(bg="#E2F1E7")
    # Title Label
    title_logo = tk.PhotoImage(file="misc\identify.png")
    title_label = Label(
        parent, text="Speaker Recognition System", font=("Segoe UI", 24, "bold"),
        bg="#E2F1E7", fg="#243642", image=title_logo, compound='right', padx=10, pady=10
    )
    title_label.image = title_logo
    title_label.pack(pady=20)

    # ML Features Function
    def extract_features():
        audio_dir = "saved_audio"
        output_dir = "model/mfcc"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        n_mfcc = 128
        for file_name in os.listdir(audio_dir):
            if file_name.endswith('.wav'):
                file_path = os.path.join(audio_dir, file_name)
                audio, sr = librosa.load(file_path, sr=None)
                audio = librosa.util.fix_length(audio, size=5 * sr)

                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
                mfcc_delta = librosa.feature.delta(mfcc)
                mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
                features = np.concatenate((mfcc, mfcc_delta, mfcc_delta2), axis=0)

                mfcc_mean = np.mean(features, axis=1)
                save_path = os.path.join(output_dir, file_name.replace('.wav', '.npy'))
                np.save(save_path, mfcc_mean)
                print(f"Saved features for {file_name} at {save_path}.")

        messagebox.showinfo("Success", "Feature extraction completed.")

    def train_model():
        feature_dir = "model/mfcc"
        if not os.path.exists(feature_dir):
            print(f"Feature directory {feature_dir} does not exist.")
            return

        model_dir = "model/modeldata"
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # Find the next available filename
        existing_files = [f for f in os.listdir(model_dir) if f.startswith("newvoicemodeldata") and f.endswith(".joblib")]
        if existing_files:
            latest_file = max(existing_files, key=lambda x: int(x[len("newvoicemodeldata"):-len(".joblib")]))
            next_index = int(latest_file[len("newvoicemodeldata"):-len(".joblib")]) + 1
        else:
            next_index = 1

        model_path = os.path.join(model_dir, f"newvoicemodeldata{next_index:02d}.joblib")

        X, y = [], []

        for file_name in os.listdir(feature_dir):
            if file_name.endswith('.npy'):
                file_path = os.path.join(feature_dir, file_name)
                mfcc = np.load(file_path)
                X.append(mfcc)
                label = ''.join([c for c in file_name if c.isalpha()])
                y.append(label)

        X, y = np.array(X), np.array(y)

        # Debug: Print label distribution
        print("Original Class Distribution:", Counter(y))

        # Balance dataset
        try:
            ros = RandomOverSampler(random_state=42)
            X, y = ros.fit_resample(X, y)
            print("Balanced Class Distribution:", Counter(y))
        except ValueError as e:
            if str(e) == "The target 'y' needs to have more than 1 class. Got 1 class instead":
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                messagebox.showerror("Error", "More than one person is required. Record more than 10 samples.")
                root.destroy()
            else:
                raise

        # Normalize features
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # Encode labels
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Hyperparameter Tuning for MLP
        param_grid = {
            'hidden_layer_sizes': [(128, 64), (256, 128, 64)],
            'alpha': [0.0001, 0.001, 0.01],
        }
        grid = GridSearchCV(MLPClassifier(max_iter=1500, random_state=42), param_grid, cv=3)
        grid.fit(X_train, y_train)
        model = grid.best_estimator_
        print("Best Parameters:", grid.best_params_)

        # Evaluate
        train_accuracy = model.score(X_train, y_train)
        test_accuracy = model.score(X_test, y_test)
        print(f"Train accuracy: {train_accuracy * 100:.2f}%")
        print(f"Test accuracy: {test_accuracy * 100:.2f}%")

        print("Classification Report:")
        predictions = model.predict(X_test)
        print(classification_report(y_test, predictions))

        print("Confusion Matrix:")
        print(confusion_matrix(y_test, predictions))

        # Save model
        joblib.dump((model, label_encoder), model_path)
        messagebox.showinfo("Success", f"Model trained and saved at {model_path}.")

    def recognize_speaker():
        model_dir = "model/modeldata"
        if not os.path.exists(model_dir):
            messagebox.showinfo("Error", "Model directory not found. Train the model first.")
            return

        model_files = [os.path.join(model_dir, f) for f in os.listdir(model_dir) if f.endswith('.joblib')]
        if not model_files:
            messagebox.showinfo("Error", "No model files found in the directory.")
            return

        # Load the latest model based on creation time
        latest_model_path = max(model_files, key=os.path.getctime)
        model, label_encoder = joblib.load(latest_model_path)

        # Recording parameters
        duration = 5  # seconds
        sample_rate = 44100
        channels = 1

        # Notify the user to start speaking
        messagebox.showinfo("Info", "Click OK and start speaking.")
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32')
        sd.wait()  # Wait until recording is finished

        audio_data = np.squeeze(audio_data)
        audio_resampled = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=sample_rate)

        mfcc = librosa.feature.mfcc(y=audio_resampled, sr=sample_rate, n_mfcc=128)
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)

        features = np.concatenate((mfcc, mfcc_delta, mfcc_delta2), axis=0)
        mfcc_mean = np.mean(features, axis=1).reshape(1, -1)

        prediction = model.predict(mfcc_mean)[0]
        speaker = label_encoder.inverse_transform([prediction])[0]
        print("Prediction Output:", prediction)
        if speaker.endswith("npy"):
            speaker = speaker[:-3]

        messagebox.showinfo("Result", f"Speaker Name: {speaker.upper()}")
  
    def generate_pie_chart():
        folder = "saved_texts"
        if not os.path.exists(folder):
            messagebox.showerror("Error", f"Folder '{folder}' not found.")
            return
        
        file_list = os.listdir(folder)
        if not file_list:
            messagebox.showinfo("Info", "No user data found.")
            return
        
        name_counter = Counter()

        for file_name in os.listdir(folder):
            if file_name.endswith(".txt"):
                base_name = ''.join([c for c in file_name if not c.isdigit()]).replace(".txt", "").strip()
                name_counter[base_name] += 1

        if not name_counter:
            messagebox.showinfo("Info", "No user found.")
            return

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(name_counter.values(), labels=name_counter.keys(), autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
        ax.set_title("Data Distribution by Name")

        for widget in parent.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        chart_canvas = FigureCanvasTkAgg(fig, parent)
        chart_widget = chart_canvas.get_tk_widget()
        chart_widget.pack(side=tk.BOTTOM, padx=10, pady=10)

        chart_widget.config(width=300, height=300)

    # Buttons
    Button(parent, text="Recognize Speaker", font=("Segoe UI", 12, "bold"),
           bg="#ffde21", fg="#000000", activebackground="#ffd900", activeforeground="#000000", command=recognize_speaker).pack(pady=5)

    Label(parent, text="-------", font=("Segoe UI", 14, "bold"), bg="#E2F1E7", fg="#E2F1E7").pack(pady=5)
    Label(parent, text="-------", font=("Segoe UI", 14, "bold"), bg="#E2F1E7", fg="#E2F1E7").pack(pady=5)
    Label(parent, text="Machine learning features", font=("Segoe UI", 15, "bold"), bg="#E2F1E7", fg="#243642").pack(pady=10)

    Button(parent, text="Show User Info", font=("Segoe UI", 10, "bold"),
           bg="#4caf50", fg="#ffffff", activebackground="#388e3c", activeforeground="#000000", command=generate_pie_chart).pack(pady=5)
    Button(parent, text="Extract Features", font=("Segoe UI", 8, "bold"),
           bg="#0a75ad", fg="#ffffff", activebackground="#05a2f5", activeforeground="#000000", command=extract_features).pack(pady=5)
    Button(parent, text="Train Model", font=("Segoe UI", 8, "bold"),
           bg="#0a75ad", fg="#ffffff", activebackground="#05a2f5", activeforeground="#000000", command=train_model).pack(pady=5)
    Button(parent, text="Exit", font=("Segoe UI", 8, "bold"),
           bg="#0a75ad", fg="#ffffff", activebackground="#05a2f5", activeforeground="#000000", command=parent.quit).pack(pady=5)

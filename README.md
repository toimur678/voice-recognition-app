```markdown
# Voice Recognition and Analysis App

This is a Python-based voice recognition and analysis application that allows users to record audio, analyze sentiment, identify speakers, and perform topic modeling on text data. The application is built using Tkinter for the GUI and integrates various machine learning and natural language processing libraries.

## Features

- **Audio Recording**: Record audio and save it as a WAV file.
- **Sentiment Analysis**: Analyze the sentiment of text data and visualize emotions.
- **Speaker Identification**: Identify speakers using machine learning models trained on audio features.
- **Topic Modeling**: Perform topic modeling on text data and visualize the results.
- **Preprocessing**: Visualize audio preprocessing steps such as trimming, spectrogram, and mel spectrogram.

## Installation

To run this application, you need to install the required Python libraries. You can do this using `pip`:

```bash
pip install -r requirements.txt
```

### Required Libraries

The following libraries are required to run the application:

```plaintext
customtkinter
pyrebase
nltk
scikit-learn
librosa
sounddevice
soundfile
matplotlib
seaborn
pandas
bertopic
speechrecognition
imblearn
joblib
```

You can install them individually using the following commands:

```bash
pip install customtkinter pyrebase nltk scikit-learn librosa sounddevice soundfile matplotlib seaborn pandas bertopic speechrecognition imblearn joblib
```

### Additional Setup

1. **NLTK Data**: Download the necessary NLTK data by running the following Python code:

    ```python
    import nltk
    nltk.download('stopwords')
    nltk.download('vader_lexicon')
    nltk.download('wordnet')
    nltk.download('punkt')
    ```

2. **Firebase Configuration**: The application uses Firebase for user authentication. You need to provide your Firebase configuration in the `misc/firebase.json` file.

3. **Email Configuration**: If you want to enable email alerts for login events, configure the email settings in the `misc/config.json` file.

## Usage

1. **Run the Application**: Start the application by running the `main.py` file:

    ```bash
    python main.py
    ```

2. **Login/Signup**: Use the login page to sign in or create a new account.

3. **Record Audio**: Navigate to the "Record" tab to record audio and save it.

4. **Analyze Sentiment**: Use the "Analyze" tab to perform sentiment analysis on text data.

5. **Identify Speakers**: Use the "Identify" tab to recognize speakers based on their voice.

6. **Topic Modeling**: Use the "Summary" tab to perform topic modeling on text data.

7. **Preprocessing**: Use the "Preprocess" tab to visualize audio preprocessing steps.

## Directory Structure

```plaintext
toimur678-voice-recognition-app/
    ├── analyze.py
    ├── identify.py
    ├── main.py
    ├── preprocess.py
    ├── record.py
    └── sentiment.py
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Acknowledgments

- [NLTK](https://www.nltk.org/) for natural language processing.
- [Librosa](https://librosa.org/) for audio analysis.
- [BERTopic](https://maartengr.github.io/BERTopic/) for topic modeling.
- [Scikit-learn](https://scikit-learn.org/) for machine learning.
```

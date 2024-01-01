# entry_script.py
import nltk
from nltk.collocations import *
from nltk.metrics import association
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet

import scipy.stats
from scipy.stats import fisher_exact
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os

os.makedirs('models', exist_ok=True)

df = pd.read_csv('data/transactions.csv')
X = df['text'].astype(str)
y = df['category']

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.15, random_state=42)

pipeline = make_pipeline(
    TfidfVectorizer(ngram_range=(1,2), min_df=1),
    LogisticRegression(max_iter=500)
)

pipeline.fit(X_train, y_train)
pred = pipeline.predict(X_test)
print('\nClassification report on test set:')
print(classification_report(y_test, pred))
joblib.dump(pipeline, 'models/tfidf_lr_expense.pkl')
print('\nSaved trained model to models/tfidf_lr_expense.pkl')

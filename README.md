# AI Expense Analyzer - Paste-SMS MVP

**What it is**
A minimal demo that classifies pasted bank/SMS transaction lines into categories (Food, Travel, Bills, Shopping, Transfer, Fuel, Other).
Uses a hybrid approach: small rules dictionary + TF-IDF + Logistic Regression.

**How to run (quick)**
1. Create virtual env:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. (Optional) Re-train model:
   ```bash
   python train_model.py
   ```
   This will create `models/tfidf_lr_expense.pkl`.

3. Run demo:
   ```bash
   python app.py
   ```
   Open http://127.0.0.1:5000 and paste SMS lines (one per line) to see categories and totals.

**Files**
- data/transactions.csv : sample labeled data used for training
- train_model.py : trains a TF-IDF + LogisticRegression model
- models/tfidf_lr_expense.pkl : pre-trained model (created by training script)
- predict.py : inference + merchant keyword rules
- app.py : minimal Flask demo UI
- requirements.txt : Python dependencies

**Resume lines (copy-paste)**
- Built a lightweight AI Expense Analyzer that parses bank SMS and classifies transactions using a hybrid rules + TF-IDF+Logistic Regression pipeline.
- Implemented a demo UI (Flask) that displays categorized transactions and monthly totals from pasted SMS lines.

**Notes**
- This is an MVP. Improve accuracy by adding more labeled examples, adding OCR for screenshots, and using sentence embeddings for better semantics.


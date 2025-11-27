import joblib, re
model = joblib.load('models/tfidf_lr_expense.pkl')

RULES = {
    'zomato': 'Food', 'swiggy':'Food', "domino":'Food', 'cafe':'Food', 'tea':'Food',
    'flipkart':'Shopping','amazon':'Shopping','myntra':'Shopping','bigbasket':'Shopping',
    'netflix':'Bills','spotify':'Bills','hotstar':'Bills','gaana':'Bills','bookmyshow':'Shopping',
    'indianoil':'Fuel','bpcl':'Fuel','shell':'Fuel',
    'uber':'Travel','ola':'Travel','bus':'Travel','metro':'Travel'
}

def rule_category(text):
    t = text.lower()
    for k,v in RULES.items():
        if k in t:
            return v
    return None

def classify(text):
    r = rule_category(text)
    if r:
        return r
    return model.predict([text])[0]

if __name__ == '__main__':
    examples = [
        "Your a/c XXXX debited by Rs 1299.50 at Zomato on 25-11-2025.",
        "INR 499 paid to Netflix subscription.",
        "Debited ₹560 at Indian Oil pump",
        "Rs 2300 credited by salary from ACME Ltd",
        "INR 350 paid at Cafe Coffee Day"
    ]
    for e in examples:
        print(e, " -> ", classify(e))

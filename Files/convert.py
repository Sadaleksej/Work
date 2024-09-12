import pandas as pd
with open('resultDiplom.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)
df.to_csv('products_sentiment_train.csv', encoding='utf-8', index=False)
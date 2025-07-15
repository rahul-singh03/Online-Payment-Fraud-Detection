import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load dataset
df = pd.read_csv("onlinefraud.csv")

df = df.sample(20000, random_state=42)

# Encode categorical variables
df['type'] = df['type'].astype('category').cat.codes
df['isFraud'] = df['isFraud'].astype(int)

# Drop unwanted cols if any
df = df.drop(columns=['nameOrig', 'nameDest'])

# Split features & labels
X = df.drop('isFraud', axis=1)
y = df['isFraud']

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "fraud_model.pkl")

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
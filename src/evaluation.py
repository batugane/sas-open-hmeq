import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

def evaluate(model, x_test, y_test):
    preds = model.predict(x_test)
    proba = model.predict_proba(x_test)
    print(confusion_matrix(y_test, preds))
    print(classification_report(y_test, preds))
    acc = np.round(model.score(x_test, y_test)*100, 2)
    print(f"Gradient Boosting Model Accuracy = {acc}%")
    return preds, proba

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import logging

logger = logging.getLogger(__name__)

def evaluate(model, x_test, y_test):
    preds = model.predict(x_test)
    proba = model.predict_proba(x_test)
    logger.info(confusion_matrix(y_test, preds))
    logger.info(classification_report(y_test, preds))
    acc = np.round(model.score(x_test, y_test)*100, 2)
    logger.info(f"Gradient Boosting Model Accuracy = {acc}%")
    return preds, proba

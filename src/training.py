import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

def train_gbc(x_train, y_train, params):
    gbc = GradientBoostingClassifier(**params)
    model = gbc.fit(x_train, y_train)
    return model

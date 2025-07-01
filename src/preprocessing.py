from sklearn.model_selection import train_test_split

def split_and_impute(df, predictors, target, test_size, random_state):
    x = df[predictors]
    y = df[target]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=random_state
    )
    # Impute missing with column means
    x_train.fillna(x_train.mean(), inplace=True)
    x_test.fillna(x_test.mean(), inplace=True)
    return x_train, x_test, y_train, y_test

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from skopt import BayesSearchCV
from skopt.space import Integer, Real
from sklearn.linear_model import LogisticRegression

import os 
import json 
import joblib

def read_dataset():
    dataset = pd.read_csv('C:/Users/Bhavin/Desktop/work/Credit Prediction/Credit-Prediction/Data/german_credit_data.csv')
    return dataset

def categorize_purpose(purpose):    
    if purpose in ['car', 'radio/TV','furniture/equipment']:
        return 'High Frequency Purpose'
    elif purpose in ['business', 'education']:
        return 'Medium Frequency Purpose'
    else:
        return 'Low Frequency Purpose'
    

# Define all possible categories for Purpose to ensure consistent columns
ALL_PURPOSE_CATEGORIES = ['High Frequency Purpose', 'Medium Frequency Purpose', 'Low Frequency Purpose']
ALL_GENDER_CATEGORIES = ['male', 'female']
def process_dataset(df):
    # Remove the columns which are not required
    df = df.drop(['Unnamed: 0'], axis=1)

    # Fill NaN values
    df['Saving accounts'] = df['Saving accounts'].fillna('no_inf')
    df['Checking account'] = df['Checking account'].fillna('no_inf')

    # Convert Age to Categories
    df['Age'] = pd.cut(df['Age'], bins=[18, 25, 40, 60, 100], labels=[0, 1, 2, 3])

    # Convert Sex to one-hot encoding
    df_sex = pd.get_dummies(df["Sex"]).astype(int)
    for category in ALL_GENDER_CATEGORIES:
        if category not in df_sex:
            df_sex[category] = 0  # Add missing columns with 0s
            
    df = pd.concat([df, df_sex], axis=1).drop(columns=["Sex"])

    # Convert Housing to Label Encoding
    housing_map = {"own": 2, "free": 0, "rent": 1}
    df['Housing'] = df['Housing'].map(housing_map)

    # Convert Saving accounts to Label Encoding
    savings_map = {"little": 1, "moderate": 2, "quite rich": 3, "rich": 4, "no_inf": 0}
    df['Saving accounts'] = df['Saving accounts'].map(savings_map)

    # Convert Checking account to Label Encoding
    checking_map = {"little": 1, "moderate": 2, "rich": 3, "no_inf": 0}
    df['Checking account'] = df['Checking account'].map(checking_map)

    # Log transform Credit amount
    df['credit_amount_log'] = np.log1p(df['Credit amount'] - df['Credit amount'].min() + 1)
    df = df.drop(columns=["Credit amount"])

    # Bucket the Duration column into categories
    df['Duration'] = pd.cut(df['Duration'], bins=[0, 12, 24, 48, 100], labels=[0, 1, 2, 3])

    # Map Purpose column to predefined categories
    df['Purpose_Category'] = df['Purpose'].apply(categorize_purpose)
    df = df.drop(columns=["Purpose"])

    # Create dummy variables for Purpose_Category with all categories ensured
    df_purpose = pd.get_dummies(df['Purpose_Category'], dtype=int)
    for category in ALL_PURPOSE_CATEGORIES:
        if category not in df_purpose:
            df_purpose[category] = 0  # Add missing columns with 0s

    # Concatenate with the main DataFrame and drop Purpose_Category
    df = pd.concat([df, df_purpose], axis=1).drop(columns=["Purpose_Category"])

    # Convert Risk to binary
    risk_map = {"good": 1, "bad": 0}
    df['Risk'] = df['Risk'].map(risk_map)

    # save column order to a file 
    column_order = list(df.columns)

    if not os.path.exists("Data/column_order.json"):

        with open("Data/column_order.json", "w") as f:
            json.dump(column_order, f)
    else:

        with open("Data/column_order.json", "r") as f:
            column_order = json.load(f)

            df = df[column_order]


    return df

def load_model(model_path):
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        return model
    else:
        return None

def train_model(df, model_path=None):
    # Split the data into train and test
    train, test = train_test_split(df, test_size=0.2, random_state=42)

    # Split the data into X and y
    X_train = train.drop(columns=["Risk"])
    y_train = train["Risk"]
    X_test = test.drop(columns=["Risk"])
    y_test = test["Risk"]

    # Load existing model if model_path is provided
    if model_path and os.path.exists(model_path):
        print(f"Loading existing model from {model_path}...")
        existing_model = joblib.load(model_path)
        y_pred_existing = existing_model.predict(X_test)
        existing_accuracy = accuracy_score(y_test, y_pred_existing)
        print("Accuracy of the existing model is:", existing_accuracy)
    else:
        existing_accuracy = 0  # No existing model or model path provided

    # Define the hyperparameter search space
    param_space = {
        'n_estimators': Integer(50, 500),
        'max_depth': Integer(5, 50),
        'min_samples_split': Integer(2, 20),
        'min_samples_leaf': Integer(1, 20),
        'max_features': Real(0.1, 1.0, prior='uniform')
    }

    # Define the Bayesian search with cross-validation
    bayes_search = BayesSearchCV(
        estimator=RandomForestClassifier(random_state=42),
        search_spaces=param_space,
        n_iter=30,  # Number of parameter settings that are sampled
        cv=3,  # Number of cross-validation folds
        scoring='accuracy',
        random_state=42,
        n_jobs=-1
    )

    # Perform Bayesian optimization
    print("Training a new model with Bayesian optimization...")
    bayes_search.fit(X_train, y_train)

    # Best model found
    best_model = bayes_search.best_estimator_
    y_pred = best_model.predict(X_test)
    new_accuracy = accuracy_score(y_test, y_pred)

    print("Accuracy of the optimized model is:", new_accuracy)
    print("Best hyperparameters:", bayes_search.best_params_)

    # Save the new model if it performs better than the existing model
    if new_accuracy > existing_accuracy:
        if(model_path == None):
            model_path = 'Models/RFModel.pkl'
        print(f"New model performs better. Saving model to {model_path}...")
        joblib.dump(best_model, model_path)
    else:
        print("Existing model performs better. Keeping the existing model.")

    # Return the best model and its accuracy
    return best_model, new_accuracy

def train_LR_model(df, model_path=None):
    # Split the data into train and test
    train, test = train_test_split(df, test_size=0.2, random_state=42)

    # Split the data into X and y
    X_train = train.drop(columns=["Risk"])
    y_train = train["Risk"]
    X_test = test.drop(columns=["Risk"])
    y_test = test["Risk"]

    # Load existing model if model_path is provided and exists
    if model_path and os.path.exists(model_path):
        print(f"Loading existing model from {model_path}...")
        existing_model = joblib.load(model_path)
        y_pred_existing = existing_model.predict(X_test)
        existing_accuracy = accuracy_score(y_test, y_pred_existing)
        print("Accuracy of the existing model is:", existing_accuracy)
    else:
        existing_accuracy = 0  # No existing model or model path provided

    # Define the hyperparameter search space
    param_space = {
        'C': Real(0.1, 10.0, prior='log-uniform'),
        'penalty': ['l2']
    }

    # Define the Bayesian search with cross-validation
    bayes_search = BayesSearchCV(
        estimator=LogisticRegression(random_state=42),
        search_spaces=param_space,
        n_iter=30,  # Number of parameter settings that are sampled
        cv=3,  # Number of cross-validation folds
        scoring='accuracy',
        random_state=42,
        n_jobs=-1
    )

    # Perform Bayesian optimization
    print("Training a new Logistic Regression model with Bayesian optimization...")
    bayes_search.fit(X_train, y_train)

    # Best model found
    best_model = bayes_search.best_estimator_
    y_pred = best_model.predict(X_test)
    new_accuracy = accuracy_score(y_test, y_pred)

    print("Accuracy of the optimized model is:", new_accuracy)
    print("Best hyperparameters:", bayes_search.best_params_)

    # Save the new model if it performs better than the existing model
    if new_accuracy > existing_accuracy:
        if(model_path == None):
            model_path = 'Models/LRModel.pkl'
        print(f"New model performs better. Saving model to {model_path}...")
        joblib.dump(best_model, model_path)
    else:
        print("Existing model performs better. Keeping the existing model.")

    # Return the best model and its accuracy
    return best_model, new_accuracy

def get_DT_feature_importances(model, X_train):
    feature_importance = model.feature_importances_
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    print(pos.size)
    print(sorted_idx.size)
    print(X_train.columns.size)
    print(X_train.columns)
    print(feature_importance)
    print(sorted_idx)
    print(feature_importance[sorted_idx])
    print(X_train.columns[sorted_idx])
    return feature_importance, sorted_idx, pos

def plot_feature_importances(feature_importance, sorted_idx, pos, X_train, Model_Name):
    plt.figure(figsize=(12, 6))
    plt.barh(pos, feature_importance[sorted_idx], align='center')
    plt.yticks(pos, X_train.columns[sorted_idx])
    plt.xlabel('Relative Importance')
    plt.title('Variable Importance for ' + Model_Name)
    plt.show()

def get_logistic_regression_feature_importances(model, X_train):
    feature_importance = np.abs(model.coef_[0])
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    print(pos.size)
    print(sorted_idx.size)
    print(X_train.columns.size)
    print(X_train.columns)
    print(feature_importance)
    print(sorted_idx)
    print(feature_importance[sorted_idx])
    print(X_train.columns[sorted_idx])
    return feature_importance, sorted_idx, pos

def main():
    dataset = read_dataset()

    dataset = process_dataset(dataset)
    
    RFmodel, RFAccuracy = train_model(dataset)

    LRModel, LRAccuracy = train_LR_model(dataset)

    # Save the models 
    joblib.dump(RFmodel, 'Models/RFModel.pkl')
    joblib.dump(LRModel, 'Models/LRModel.pkl')

    # Get the feature importances
    feature_importance_RF, sorted_idx_RF, pos_RF = get_DT_feature_importances(RFmodel, dataset.drop(columns=["Risk"]))
    feature_importance_LR, sorted_idx_LR, pos_LR = get_logistic_regression_feature_importances(LRModel, dataset.drop(columns=["Risk"]))

    # Save the feature importances
    np.save('FeatureImportances/RF_feature_importance.npy', feature_importance_RF)
    np.save('FeatureImportances/RF_sorted_idx.npy', sorted_idx_RF)

    np.save('FeatureImportances/LR_feature_importance.npy', feature_importance_LR)
    np.save('FeatureImportances/LR_sorted_idx.npy', sorted_idx_LR)

    # Plot the feature importances
    plot_feature_importances(feature_importance_RF, sorted_idx_RF, pos_RF, dataset.drop(columns=["Risk"]), "Random Forest")
    plot_feature_importances(feature_importance_LR, sorted_idx_LR, pos_LR, dataset.drop(columns=["Risk"]), "Logistic Regression")
    

    print("Feature importances saved successfully")





if __name__ == "__main__":

    main()




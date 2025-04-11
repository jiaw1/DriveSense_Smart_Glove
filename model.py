import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

# Load datasets
train_df = pd.read_csv("train.csv")
val_df = pd.read_csv("val.csv")
test_df = pd.read_csv("test.csv")

# Parameters
window_size = 25
stride = 2

# Create sliding windows
def create_windows(df, window_size, stride):
    windows = []
    labels = []
    for start in range(0, len(df) - window_size, stride):
        end = start + window_size
        window = df.iloc[start:end]
        sensor_values = window.drop(columns=["label"]).values.flatten()
        windows.append(sensor_values)
        labels.append(window['label'].iloc[0])
    return np.array(windows), np.array(labels)

# Prepare data
X_train, y_train = create_windows(train_df, window_size, stride)
X_val, y_val = create_windows(val_df, window_size, stride)
X_test, y_test = create_windows(test_df, window_size, stride)

# Show label distribution
print("Label Distribution in Training Set:", Counter(y_train))
print("Label Distribution in Validation Set:", Counter(y_val))
print("Label Distribution in Test Set:", Counter(y_test))

# Define SVM and parameter grid
svm_model = SVC(class_weight='balanced')
param_grid = {
    'model__C': [0.1, 1, 10],
    'model__kernel': ['linear', 'rbf', 'poly']
}

# Create pipeline and tune
pipe = Pipeline([('scaler', StandardScaler()), ('model', svm_model)])
grid = GridSearchCV(pipe, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1)

print("\nTraining and tuning SVM...")
grid.fit(X_train, y_train)
best_svm = grid.best_estimator_

# Show best parameters
svm_clf = best_svm.named_steps['model']
print("\nBest SVM Parameters:")
print(f"Kernel: {svm_clf.kernel}")
print(f"C: {svm_clf.C}")
print(f"Gamma: {getattr(svm_clf, 'gamma', 'N/A')}")
print(f"Degree (if poly): {getattr(svm_clf, 'degree', 'N/A')}")

# Predictions
y_pred_val = best_svm.predict(X_val)
y_pred_test = best_svm.predict(X_test)

# Accuracy
val_acc = accuracy_score(y_val, y_pred_val)
test_acc = accuracy_score(y_test, y_pred_test)

# Reports
print("\nSVM Classification Report (Validation):")
print(classification_report(y_val, y_pred_val, digits=4))

print("SVM Classification Report (Test):")
print(classification_report(y_test, y_pred_test, digits=4))

print(f"SVM Validation Accuracy: {val_acc:.4f}")
print(f"SVM Test Accuracy: {test_acc:.4f}")

# Per-class recognition accuracy
cm = confusion_matrix(y_test, y_pred_test)
class_accuracy = cm.diagonal() / cm.sum(axis=1)

print("\nPer-Class Recognition Accuracy (Test):")
for label, acc in zip(np.unique(y_test), class_accuracy):
    print(f"Class {label}: {acc:.2%}")

# Confusion matrix plot
labels = np.unique(y_test)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('SVM Confusion Matrix (Test Set)')
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=300)
plt.close()
print("Confusion matrix saved as 'confusion_matrix.png'")

# Save classification report to file
with open("svm_classification_report.txt", "w") as f:
    f.write("SVM Classification Report (Validation Set):\n")
    f.write(classification_report(y_val, y_pred_val, digits=4))
    f.write("SVM Classification Report (Test Set):\n")
    f.write(classification_report(y_test, y_pred_test, digits=4))
    f.write(f"SVM Validation Accuracy: {val_acc:.4f}")
    f.write(f"SVM Test Accuracy: {test_acc:.4f}")

print("Classification report saved as 'classification_report.txt'")

# Save the model
joblib.dump(best_svm, 'svm_model.pkl')
print("Best SVM model saved as 'svm_model.pkl'")

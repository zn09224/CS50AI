import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

def converted_value(i, value):
    
    months = {"Jan": 0, "Feb": 1, "Mar": 2, "April": 3, "May": 4, "June": 5,
              "Jul": 6, "Aug": 7, "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11}
    
    if i == 1 or i == 3 or i == 5 or i == 6 or i == 7 or i == 8 or i == 9:
        return float(value)
    elif i == 15:
        if value == "Returning_Visitor":
            return 1
        else:
            return 0
    elif i == 16 or i == 17:
        if value == "TRUE":
            return 1
        else:
            return 0
    elif i == 10:
        return months[value]
    else:
        return int(value)

def load_data(filename):
    
    with open(filename, mode = 'r') as data:
        data = csv.reader(data)
        data = list(data)

        evidence = []
        labels = []
        
        for row in data[1:]:
            convertedRow = [converted_value(i, value) for i, value in enumerate(row)]
            evidence.append(convertedRow[:-1])
            labels.append(convertedRow[-1])
        
        return (evidence, labels)   
    

def train_model(evidence, labels):
    
    knn = KNeighborsClassifier(n_neighbors = 1)
    knn.fit(evidence, labels)
    return knn


def evaluate(labels, predictions):
    
    identifiedPositiveLabels = 0
    identifiedNegativeLabels = 0
    actualPosLabels = 0
    actualNegLabels = 0
    
    for label, prediction in zip(labels, predictions):
        
        if label == 1:
            if prediction == 1:
                identifiedPositiveLabels += 1
            actualPosLabels += 1
            
        elif label == 0:
            if prediction == 0:
                identifiedNegativeLabels += 1
            actualNegLabels += 1
            
    sensitivity = identifiedPositiveLabels / actualPosLabels
    specificity = identifiedNegativeLabels / actualNegLabels
    
    return (sensitivity, specificity)

if __name__ == "__main__":
    main()

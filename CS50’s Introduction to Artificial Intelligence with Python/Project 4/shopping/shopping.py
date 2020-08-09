import csv
import sys
import pandas as pd

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


def convert_month_to_number(month):
    if month == 'Jan':
        return 0
    elif month == 'Feb':
        return 1
    elif month == 'Mar':
        return 2
    elif month == 'Apr':
        return 3
    elif month == 'May':
        return 4
    elif month == 'Jun':
        return 5
    elif month == 'Jul':
        return 6
    elif month == 'Aug':
        return 7
    elif month == 'Sep':
        return 8
    elif month == 'Oct':
        return 9
    elif month == 'Nov':
        return 10
    elif month == 'Dec':
        return 11
    else:
        return -1


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    data = pd.read_csv(filename)

    labels = data['Revenue'].map(lambda x: 1 if x is True else 0).tolist()

    data['Month'] = data['Month'].map(lambda x: convert_month_to_number(x))
    data.drop(data[data['Month'] == -1].index)

    data['VisitorType'] = data['VisitorType'].map(lambda x: 1 if x == 'Returning_Visitor' else 0)
    data['Weekend'] = data['Weekend'].map(lambda x: 1 if x is True else 0)

    for i in data.keys():
        if i == 'Administrative' or i == 'Informational' or i == 'ProductRelated' or i == 'OperatingSystems' or \
                i == 'Browser' or i == 'Region' or i == 'TrafficType' or i == 'VisitorType' or i == 'Weekend':
            if not pd.api.types.is_integer_dtype(data[i].dtype):
                data = data[i].apply(lambda x: not isinstance(x, int))
        if i == 'Administrative_Duration' or i == 'Informational_Duration' or i == 'ProductRelated_Duration' or \
                i == 'BounceRates' or i == 'ExitRates' or i == 'PageValues' or i == 'SpecialDay':
            if not pd.api.types.is_float_dtype(data[i].dtype):
                data = data[data[i].apply(lambda x: isinstance(x, float))]
    data.drop("Revenue", axis=1, inplace=True)
    evidence = data.values.tolist()
    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    actual_positive = 0
    actual_negative = 0
    predicted_positive = 0
    predicted_negative = 0
    for i, j in zip(labels, predictions):
        if i == 1:
            actual_positive += i
            predicted_positive += j
        else:
            actual_negative += 1
            if j == 0:
                predicted_negative += 1
    return predicted_positive/actual_positive, predicted_negative/actual_negative


if __name__ == "__main__":
    main()

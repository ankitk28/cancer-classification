import numpy as np
import pandas as pd
import os
import argparse
from tqdm import tqdm
import logging

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score

from sklearn.feature_selection import mutual_info_classif, f_classif
from sklearn.feature_selection import SelectKBest, SelectPercentile, SelectFromModel

from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from sklearn import metrics

import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO)


class ModelUtilities:
    def __init__(self, X_train, Y_train, X_test, Y_test):
        self.X_train = X_train
        self.Y_train = Y_train
        self.X_test = X_test
        self.Y_test = Y_test

    def get_important_features(self, method, number_of_features):
        if method is 'select_k_best':
            best_indices = SelectKBest(k=number_of_features, score_func=f_classif).fit(
                self.X_train, self.Y_train).get_support(indices=True)
            return best_indices

    def test_for_all(data):
        from collections import defaultdict
        scores = defaultdict(list)
        for nf in range(5, 51):
            for k in range(1, 21):
                best_features = self.get_important_features(
                    self.X_train, self.Y_train, 'select_k_best', nf)
                tr_acc, test_acc = self.build_nearest_neighbor_model(self, k, best_features)
                scores[nf].append(test_acc)
        return scores


def get_kbest_features(X_train, Y_train, number_of_features):
    best_indices = SelectKBest(k=number_of_features, score_func=f_classif).fit(
        X_train, Y_train).get_support(indices=True)
    return best_indices


def build_nearest_neighbor_model(X_train, Y_train, k=5, feature_indices=None):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]

    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, Y_train)

    return model


def build_svm_model(X_train, Y_train, feature_indices=None, kernel='rbf'):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]

    model = svm.SVC(C=1.0, kernel=kernel, gamma=0.01, random_state=1405)
    model.fit(X_train, Y_train)

    return model


def build_naive_bayes_model(X_train, Y_train, feature_indices=None):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]

    model = GaussianNB()
    model.fit(X_train, Y_train)

    return model


def build_random_forest_model(X_train, Y_train, feature_indices=None, n_trees=20):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]

    model = RandomForestClassifier(n_estimators=n_trees)
    model.fit(X_train, Y_train)

    return model


def build_logistic_regression_model(X_train, Y_train, feature_indices=None):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]

    model = LogisticRegression(random_state=1405, solver='lbfgs')
    model.fit(X_train, Y_train)

    return model


def calculate_accuracies(X_train, Y_train, X_test, Y_test, model, feature_indices=None):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]
        X_test = X_test[:, feature_indices]

    train_pred_y = model.predict(X_train)
    test_pred_y = model.predict(X_test)

    train_accuracy = metrics.accuracy_score(y_pred=train_pred_y, y_true=Y_train)
    test_accuracy = metrics.accuracy_score(y_pred=test_pred_y, y_true=Y_test)

    return train_accuracy, test_accuracy


def plot_roc_curve(X_train, Y_train, X_test, Y_test, model, feature_indices=None):
    if feature_indices is not None:
        X_train = X_train[:, feature_indices]
        X_test = X_test[:, feature_indices]

    train_pred_y = model.predict(X_train)
    test_pred_y = model.predict(X_test)
    fpr, tpr, threshold = metrics.roc_curve(Y_test, test_pred_y)
    roc_auc = metrics.auc(fpr, tpr)
    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()

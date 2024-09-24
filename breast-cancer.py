import numpy as np
import argparse

from sklearn.model_selection import train_test_split

from CrossValidation import validation, print_best_model
from dataset.breast_cancer_classification.preprocess_breast_cancer import breast_cancer_dataset, \
    convert_to_numeric_array
from dataset.fashion_mnist_classification.preprocess_fashion_mnist import shuffle_data
from neural_network.DenseLayer import DenseLayer
from neural_network.Model import Model
from neural_network.activation_functions.ReluActivationFunction import Relu
from neural_network.activation_functions.SoftmaxActivationFunction import Softmax
from neural_network.loss_functions.LossCategoricalCrossEntropy import LossCategoricalCrossEntropy
from neural_network.metrics_implementations.AccuracyCategorical import AccuracyCategorical
from neural_network.metrics_implementations.F1_score import compare_test
from neural_network.optimizers.RmsProp import Rmsprop
from neural_network.regularization.Dropout import Dropout
from neural_network.regularization.EarlyStopping import EarlyStopping
from utils.Graphic import print_confusion_matrix, plot_training_metrics


def train_and_validate(X_train, y_train, n_output=2, number_of_folders=5, epochs=30, multithread=True):
    """
    Esegue la validazione sul training set usando la cross-validation.

    :param X_train: Set di dati di addestramento
    :param y_train: Etichette del set di dati di addestramento
    :param n_output: Numero di neuroni di uscita del modello (es. 2 per classificazione binaria)
    :param number_of_folders: Numero di fold per la cross-validation
    :param epochs: Numero di epoche per l'addestramento
    :param multithread: Abilitare o meno il multithreading
    :return: Modello ottimale dopo la cross-validation
    """

    # Valida il modello con cross-validation
    best_model = validation(X_train, y_train, n_output=n_output, number_of_folders=number_of_folders, epochs=epochs,
                            multithread=multithread)

    # Restituisci il miglior modello trovato
    print_best_model(best_model['model'])
    return best_model


def retrain_and_evaluate(X_train, X_test, y_train, y_test):
    """
    Riaddestra il miglior modello sull'intero training set e lo valuta sul test set.

    :param X_train: Set di dati di addestramento
    :param X_test: Set di dati di test
    :param y_train: Etichette del set di dati di addestramento
    :param y_test: Etichette del set di dati di test
    :return: Statistiche delle performance del modello (accuracy, precision, recall, f1_score)
    """

    # ===== STRUTTURA DELLA MIGLIOR RETE NEURALE =====

    best_model_retrained = Model()
    best_model_retrained.add_layer(DenseLayer(X_train.shape[1], 64, initialization="He"))
    best_model_retrained.add_layer(Relu())
    best_model_retrained.add_layer(Dropout(0.2))
    best_model_retrained.add_layer(DenseLayer(64, 32, initialization="He"))
    best_model_retrained.add_layer(Relu())
    best_model_retrained.add_layer(Dropout(0.2))
    best_model_retrained.add_layer(DenseLayer(32, 2, initialization="He"))
    best_model_retrained.add_layer(Softmax())

    best_model_retrained.set(loss=LossCategoricalCrossEntropy(),
                             optimizer=Rmsprop(learning_rate=0.01, decay=0.0001),
                             accuracy=AccuracyCategorical(),
                             early_stopping=EarlyStopping(patience=10, min_delta=0.001))

    best_model_retrained.finalize()

    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)

    loss_history, _, _, _ = best_model_retrained.train(X_train, y_train, val_data=(X_val, y_val), epochs=100, batch_size=64, print_every=100, history=True)


    # Testiamo il modello sul Test Set
    y_pred = best_model_retrained.predict(X_test)
    y_pred = np.argmax(y_pred, axis=1)

    # Confronta le previsioni con le etichette reali
    accuracy, precision, recall, f1_score = compare_test(y_pred, y_test)

    # Stampa i risultati
    print("\n========== Stats of the Best Model on the Test Set ==========\n ")
    print("Mean Accuracy: ", accuracy)
    print("Mean Precision: ", precision)
    print("Mean Recall: ", recall)
    print("Mean F1_Score: ", f1_score)

    # Stampa la matrice di confusione
    print_confusion_matrix(y_test, y_pred)

    # Restituisci le statistiche
    return accuracy, precision, recall, f1_score


def main():
    # Caricamento del dataset
    X_train, X_test, y_train, y_test = breast_cancer_dataset()
    X_train, y_train = shuffle_data(X_train, y_train)
    X_test, y_test = shuffle_data(X_test, y_test)

    # Conversione delle etichette in formato numerico
    y_train = convert_to_numeric_array(y_train)
    y_test = convert_to_numeric_array(y_test)

    # Parsing degli argomenti da linea di comando
    parser = argparse.ArgumentParser(description="Addestramento e valutazione di una rete neurale.")
    parser.add_argument("mode", choices=["crossvalidation", "test"],
                        help="Seleziona 'crossvalidation' per eseguire la cross-validation o 'test' per eseguire il test sul test set.")
    args = parser.parse_args()

    if args.mode == "crossvalidation":
        # 1. Esegui la validazione
        train_and_validate(X_train, y_train)
        print("\nCross-validation completata, miglior modello trovato.")

    elif args.mode == "test":
        retrain_and_evaluate(X_train, X_test, y_train, y_test)
        print("\nTest completato.")


if __name__ == "__main__":
    main()

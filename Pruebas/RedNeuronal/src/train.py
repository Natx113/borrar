import os
import sys
import numpy as np
import cv2 as cv
from cv2 import ml 
import pandas as pd

def sy_feature_and_label_matrix_read(filename: str) -> np.ndarray:
    """
    Lee un archivo CSV que contiene características y etiquetas.
    - Se asume que la primera línea es la cabecera (y se descarta).
    - La última columna se considera la etiqueta.
    Retorna la matriz completa (NumPy array o Mat de OpenCV)
    """
    print(f"\nCargando matriz de características y etiquetas \"{filename}\".")
    
    if not os.path.exists(filename):
        print(f"sy_feature_and_label_matrix_read(): Error al leer el archivo de entrada: {filename}")
        sys.exit(1) # Salir del programa
    
    # Usamos Pandas para una lectura de CSV más robusta y fácil.
    # header=None se usa si el archivo no tiene cabeceras. 
    # Si el archivo TIENE cabecera, simplemente se usa `pd.read_csv(filename)`.
    try:
        df = pd.read_csv(filename)
    except Exception as e:
        print(f"Error al leer el CSV: {e}")
        sys.exit(1)
        
    # Convertir el DataFrame de Pandas a una matriz de NumPy de tipo float32
    # que es el tipo preferido por OpenCV para datos de entrenamiento.
    full_feature_mat = df.to_numpy(dtype=np.float32)

    rows = full_feature_mat.shape[0]
    cols = full_feature_mat.shape[1]
    n_data_read = rows * cols 
    print(f"Matriz de características cargada con {rows} muestras ({n_data_read} datos).\n")
    
    return full_feature_mat

def sy_im_shuffle_rows(src: np.ndarray) -> np.ndarray:
    """ Mezcla (shuffle) las filas de una matriz utilizando numpy.random.shuffle. """
    # Creamos una copia para no modificar el original
    dst = src.copy() 
    np.random.shuffle(dst)
    return dst

def sy_feature_and_label_matrix_split(full_feature_mat: np.ndarray, n_folds: int) -> tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    """
    Divide la matriz completa en conjuntos de entrenamiento y prueba (k-fold).
    Retorna trainMat, trainLabelsMat, testMat, testLabelsMat.
    """
    if full_feature_mat.size == 0:
        print("\nMatriz de Características y Etiquetas Vacía.\n")
        return None, None, None, None
    
    # 1. Mezclar filas
    shuffled = sy_im_shuffle_rows(full_feature_mat)

    # 2. Definir divisiones
    n_samples = shuffled.shape[0]
    
    n_samples_per_fold = n_samples // n_folds
    n_samples_learn = n_samples_per_fold * (n_folds - 1)
    n_samples_test = n_samples - n_samples_learn
    
    print(f"Para prueba de {n_folds}-fold: {n_samples_per_fold} muestras por fold; "
          f"{n_samples_learn} para aprendizaje, {n_samples_test} para prueba.\n")
    
    # 3. División usando slicing de NumPy
    # Los datos (características) son todas las columnas excepto la última.
    # Las etiquetas son solo la última columna.
    
    # Conjunto de Entrenamiento (Filas de 0 a n_samples_learn; Columnas de 0 a penúltima)
    train_mat = shuffled[ :n_samples_learn, :-1]
    # Conjunto de Prueba (Filas de n_samples_learn hasta el final; Columnas de 0 a penúltima)
    test_mat = shuffled[ n_samples_learn:, :-1]
    
    # Etiquetas de Entrenamiento (Filas de 0 a n_samples_learn; Columna final)
    # Se hace 'reshape' a (-1, 1) para mantener la forma de una columna vertical, 
    # similar a una cv::Mat de 1 columna.
    train_labels_mat = shuffled[ :n_samples_learn, -1].reshape(-1, 1).astype(np.uint8)
    # Etiquetas de Prueba (Filas de n_samples_learn hasta el final; Columna final)
    test_labels_mat = shuffled[ n_samples_learn:, -1].reshape(-1, 1).astype(np.uint8)
    
    # # 4. Convertir etiquetas a CV_8UC1 (np.uint8) como requiere el código C++ original.
    # train_labels_mat = train_labels_mat.astype(np.uint8)
    # test_labels_mat = test_labels_mat.astype(np.uint8)
    
    return train_mat, train_labels_mat, test_mat, test_labels_mat


def sy_ann_mlp_train_and_test(train_mat: np.ndarray, train_labels_mat: np.ndarray, test_mat: np.ndarray, test_labels_mat: np.ndarray)-> tuple[np.ndarray,float]:
    """
    Entrena y prueba la Red Neuronal Artificial (ANN_MLP) de OpenCV.
    Retorna la matriz de confusión y la precisión.
    """
    # --- 1. CONFIGURACIÓN DEL ANN_MLP ---
    print("\nInicializando ANN_MLP\n")
    ann = ml.ANN_MLP_create()
    n_features = train_mat.shape[1] # Esto sera 27
    # El número de clases (se puede obtener de las etiqutas de entrenamiento)
    n_classes = 5                   # Fijado a 5 debido a las emociones del data set

    # Definición de capas    
    # En Python de OpenCV, se puede usar una lista o array de NumPy para las capas
    layer_sizes = np.array( [n_features, n_features * 2 + 1, n_classes], dtype=np.int32 )
    # Funciones que se autodescriben:
    ann.setLayerSizes( layer_sizes )
    ann.setActivationFunction( ml.ANN_MLP_SIGMOID_SYM, 1.0, 1.0 )
    ann.setTermCriteria( (cv.TERM_CRITERIA_MAX_ITER + cv.TERM_CRITERIA_EPS, 500, 0.00001) )
    ann.setTrainMethod( ml.ANN_MLP_BACKPROP, 0.001, 0.1 )

    # --- 2. PREPARACIÓN DE ETIQUETAS (ONE-HOT ENCODING) ---
    # ann requiere 'one-hot' encoding: una matriz de tamaño [Muestras x Clases] con '1.0' en la columna de la clase correcta.
    train_classes = np.zeros( (train_mat.shape[0], n_classes), dtype=np.float32)
    
    # Llenar la matriz one-hot. 
    # La columna de la clase correcta es la etiqueta (label) de esa fila.
    # train_labels_mat.flatten() convierte la columna vertical en un array 1D para indexación.
    labels_1d = train_labels_mat.flatten().astype(int)
    # Establecer 1.0 en la columna indexada por la etiqueta de cada fila.
    train_classes[ np.arange( train_mat.shape[0] ), labels_1d ] = 1.0
    
    print(f"\nTamaño de datos de entrenamiento: {train_mat.shape}"
          f"\nTamaño de clases de entrenamiento (one-hot): {train_classes.shape}\n")

    # --- 3. ENTRENAMIENTO ---
    print("Entrenando la ANN... (por favor, espere)\n\n\n")
    ann.train(train_mat, ml.ROW_SAMPLE, train_classes)
    
    # # Guardar el modelo
    modelo_path = "models/ANN_Music_Model.yml"
    os.makedirs("models", exist_ok=True)
    ann.save(modelo_path)
    # ann.save("ANN_Model_de_hoy.yml")

    # --- 4. PRUEBA ---
    print("Prueba de predicción ANN\n")
    
    # Matriz de confusión inicializada
    confusion = np.zeros( (n_classes, n_classes), dtype = np.int32 )

    # El método predict de OpenCV es bastante eficiente. Se puede pasar toda la matriz de prueba.
    # El segundo argumento (predictions) es el contenedor de salida.
    _, predicted_output = ann.predict( test_mat )
    
    # predicted_output es la salida de la última capa (logits/probabilidades).
    # La predicción final es el índice de la clase con la probabilidad más alta.
    predictions = np.argmax(
        predicted_output, axis=1)
    
    # Obtener las etiquetas verdaderas para comparación
    truths = test_labels_mat.flatten().astype(int)
    
    # Rellenar la matriz de confusión (usando NumPy para eficiencia)
    for truth, pred in zip(truths, predictions):
        confusion[truth, pred] += 1
    
    # Cálculo de la exactitud
    correct = np.diag( confusion )
    accuracy = correct.sum() / confusion.sum()
    
    return confusion, accuracy

def sy_feature_and_label_matrix_2_MLP( filename_feature_and_label: str, n_folds: int )-> tuple[np.ndarray,float]:
    """
    Lee un archivo de características y etiquetas y se crea una Red Neuronal 
    Artificial (ANN_MLP, de OpenCV), que se entrena y se prueba.
    Retorna la matriz de confusión y la precisión.
    """
    
    # 1. Leer archivo
    full_feature_mat = sy_feature_and_label_matrix_read( filename_feature_and_label )
    
    # 2. Dividir
    train_mat, train_labels_mat, test_mat, test_labels_mat = sy_feature_and_label_matrix_split(
        full_feature_mat, n_folds)

    # Mostrar tamaños (usando .shape de NumPy)
    print("--- Tamaños de Matrices ---")
    print(f"Tamaño de matriz de características completa: {full_feature_mat.shape}")
    print(f"Tamaño de matriz de datos de entrenamiento: {train_mat.shape}")
    print(f"Tamaño de matriz de etiquetas de entrenamiento: {train_labels_mat.shape}")
    print(f"Tamaño de matriz de datos de prueba: {test_mat.shape}")
    print(f"Tamaño de matriz de etiquetas de prueba: {test_labels_mat.shape}")
    print("--------------------------")

    # 3. Crear, Entrenar y Probar un Perceptrón Multicapa
    confusion, accuracy = sy_ann_mlp_train_and_test( 
        train_mat, train_labels_mat, 
        test_mat, test_labels_mat )
    return confusion, accuracy


def main():
    """
    Se lee un archivo de características y etiquetas y se crea una Red Neuronal 
    Artificial (ANN_MLP, de OpenCV), que se entrena y se prueba.
    Se muestan tanto la matriz de confusión como la precisión obtenida.
    """
    
    # --- CONFIGURACIÓN GENERAL ---
    filename_feature_and_label = "data/processed/mi_music_dataset_scaled.csv" 
    # filename_feature_and_label = "../ref_features/digitsHOG100.csv"  # Ejemplo de archivo
    
    # filename_feature_and_label = "HuMoments_shape.csv"  # Ejemplo de archivo
     
    n_folds = 10  # Número de particiones para la prueba de clasificación
    # --- FIN DE CONFIGURACIÓN ---

    print(f"\n\nSe lee el archivo {filename_feature_and_label} y se parten los datos en {n_folds} grupos,")
    print(f"usando {n_folds-1} para entrenar una red del tipo ANN_MLP y el grupo restante para probarla.")


    # --- FUNCIÓN TODO-EN-UNA ---
    confusion, accuracy = sy_feature_and_label_matrix_2_MLP( filename_feature_and_label, n_folds )    
    print("Matriz de confusión:\n", confusion)
    print(f"\nExactitud: {accuracy}\n")


if __name__ == "__main__":
    main()
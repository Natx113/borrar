import os
import sys
import numpy as np
import cv2 as cv
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Importamos tu extractor directamente desde tu script de entrenamiento
from src.extractor import extraer_caracteristicas_de_audio

def cargar_modelo_y_escalador():
    """ Carga la red de OpenCV y entrena el escalador usando el CSV crudo original. """
    modelo_path = "models/ANN_Music_Model_972.yml"
    csv_crudo_path = "data/processed/mi_music_dataset.csv"
    
    if not os.path.exists(modelo_path):
        print(f"Error: No se encontró el modelo en '{modelo_path}'.")
        print("Por favor, ejecuta primero src/train.py para generarlo.")
        sys.exit(1)
        
    if not os.path.exists(csv_crudo_path):
        print(f"Error: No se encontró el dataset crudo en '{csv_crudo_path}' para calibrar el escalador.")
        sys.exit(1)
        
    # 1. Cargar la Red Neuronal de OpenCV
    print("Cargando Perceptrón Multicapa desde el archivo .yml...")
    ann = cv.ml.ANN_MLP_load(modelo_path)
    
    # 2. Recrear y entrenar el Escalador al vuelo
    print("Calibrando las reglas de normalización con el dataset original...")
    df_crudo = pd.read_csv(csv_crudo_path)
    X_crudo = df_crudo.drop(columns=['label'])
    
    scaler = StandardScaler()
    scaler.fit(X_crudo) # El escalador se aprende las medias y varianzas exactas
    print("¡Escalador calibrado y listo para usar!\n")
    
    return ann, scaler

def evaluar_clip_musical(ruta_audio, ann, scaler):
    """ El core de la prueba: Extrae, normaliza y predice la emoción del audio. """
    if not os.path.exists(ruta_audio):
        print(f"\n[ERROR] No se encontró el archivo de audio en: {ruta_audio}")
        return
        
    print(f"\nAnalizando el archivo: {os.path.basename(ruta_audio)}...")
    
    # Extraer las 27 características crudas del clip
    vector_crudo = extraer_caracteristicas_de_audio(ruta_audio)
    
    if vector_crudo is None:
        print("No se pudieron extraer las características del audio.")
        return
        
    # Convertirlo a DataFrame de Pandas con los mismos nombres de columnas
    # Esto elimina por completo el Warning de StandardScaler
    vector_2d = vector_crudo.reshape(1, -1)
    columnas_nombres = [f"f_{i}" for i in range(27)] 
    
    # para clonar los nombres exactos automáticamente:
    df_para_escalar = pd.DataFrame(vector_2d, columns=scaler.feature_names_in_)
    
    # Aplicar la normalización calibrada
    vector_normalizado = scaler.transform(df_para_escalar)
    vector_listo = vector_normalizado.astype(np.float32)  # Formato estricto OpenCV
    
    # Inyectar el vector a la Red Neuronal
    _, predicted_output = ann.predict(vector_listo)
    
    # Obtener el índice de la neurona con el valor más alto
    clase_predicha = np.argmax(predicted_output, axis=1)[0]
    
    match clase_predicha:
        case 0:
            clase = "Aggressive"
        case 1:
            clase = "Dramatic"
        case 2:
            clase = "Happy"
        case 3:
            clase = "Romantic"
        case 4:
            clase = "Sad"

    # Calcular el porcentaje de certeza real (Softmax manual)
    exp_out = np.exp(predicted_output - np.max(predicted_output))
    probabilidades = exp_out / np.sum(exp_out)
    certeza = probabilidades[0][clase_predicha] * 100
    
    print("\n================== RESULTADO DE LA IA ==================")
    print(f"» Emoción Detectada: {clase}")
    # print(f"» Certeza del Modelo: {certeza:.2f}%")
    print("========================================================")

def mostrar_menu():
    # Inicializamos los componentes una sola vez al encender el menú
    ann, scaler = cargar_modelo_y_escalador()
    
    CARPETA_TEST = "data/clips_prueba"
    
    while True:
        print("\n" + "="*50)
        print("   CLASIFICADOR DE AUDIO (MLP)  ")
        print("="*50)
        print("1) Probar Clip 1 (Chop Suey! - System of a Down)")
        print("2) Probar Clip 2 (Welcome to the Black Parade - My Chemical Romance)")
        print("3) Probar Clip 3 (Designer Music - Lipps, Inc.)")
        print("4) Probar Clip 4 (In the End - Linkin Park)")
        print("5) Probar Clip 5 (Love Story - Indila(Instrumental))")
        print("6) Ingresar ruta de un archivo personalizado (.mp3/.wav)")
        print("7) Salir del programa")
        print("="*50)
        
        opcion = input("Selecciona una opción (1-7): ")
        
        if opcion == "1":
            evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip1.mp3"), ann, scaler)
        elif opcion == "2":
            evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip2.mp3"), ann, scaler)
        elif opcion == "3":
            evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip3.mp3"), ann, scaler)
        elif opcion == "4":
            evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip4.mp3"), ann, scaler)
        elif opcion == "5":
            # evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip5.mp3"), ann, scaler)
            evaluar_clip_musical(os.path.join(CARPETA_TEST, "clip5.wav"), ann, scaler)
        elif opcion == "6":
            ruta_custom = input("\nIntroduce la ruta de tu archivo de audio: ")
            ruta_custom = ruta_custom.strip("'\"") # Limpia comillas si arrastran el archivo
            evaluar_clip_musical(ruta_custom, ann, scaler)
        elif opcion == "7":
            print("\nCerrando el sistema de pruebas. ¡Hasta luego!")
            break
        else:
            print("\nOpción no válida. Intenta de nuevo.")
            
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    mostrar_menu()


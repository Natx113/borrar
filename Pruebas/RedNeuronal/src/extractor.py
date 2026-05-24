import os
import librosa
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def extraer_caracteristicas_de_audio(ruta_audio, sr=22050):
    try:
        # Cargar el archivo de audio (forzando la tasa de muestreo de Kaggle)
        y, sr = librosa.load(ruta_audio, sr=sr)
        
        # Si el audio está completamente vacío, saltarlo
        if len(y) == 0:
            return None

        # Extracción de MFCCs (13 coeficientes)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        # Sacamos el promedio de cada uno de los 13 coeficientes a lo largo del tiempo
        mfccs_mean = np.mean(mfccs, axis=1)

        #Extraccion del chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr) #Se escribe así debido a que y y sr ya son nombres definidos por la funcion
        chroma_mean = np.mean(chroma, axis=1)
        
        #Extracción de Zero Crossing Rate (Tasa de cruce por cero)
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)
        
        # Extracción de Energía (RMS - Root Mean Square Energy)
        rms = librosa.feature.rms(y=y)
        rms_mean = np.mean(rms)
        
        # Combinar todo en un solo vector numérico (Fila de Excel)
        # Unimos las 13 medias de MFCC + 12 de chroma + 1 media de ZCR + 1 media de RMS = 27 columnas
        vector_caracteristicas = np.hstack([mfccs_mean, chroma_mean, zcr_mean, rms_mean])
        
        return vector_caracteristicas

    except Exception as e:
        print(f"Error procesando {ruta_audio}: {e}")
        return None

def generar_dataset_csv(directorio_raiz, ruta_salida_csv):
    datos_completos = []
    
    # Columnas del nuevo CSV
    columnas = [f"mfcc_{i+1}" for i in range(13)] + [f"chroma_{i+1}" for i in range(12)] + ["zero_crossing_rate", "rms_energy", "label"]

    print("Calculando el tamaño total del dataset...")
    total_archivos = 0
    for emocion in os.listdir(directorio_raiz):
        ruta_emocion = os.path.join(directorio_raiz, emocion)
        if os.path.isdir(ruta_emocion):
            # Contamos solo los archivos que tengan extensiones válidas
            total_archivos += len([f for f in os.listdir(ruta_emocion) if f.endswith(('.mp3', '.wav', '.flac'))])
            
    print(f"Se encontraron {total_archivos} archivos de audio en total.\n")
    
    # Variable para llevar el conteo actual
    contador = 0

    print("Iniciando la extracción de características. Esto puede tomar tiempo...")
    
    # Recorrer las subcarpetas (cada subcarpeta es una emoción/etiqueta)
    for emocion in os.listdir(directorio_raiz):
        ruta_emocion = os.path.join(directorio_raiz, emocion)
        
        # Asegurarnos de que sea una carpeta y no un archivo suelto
        if os.path.isdir(ruta_emocion):
            print(f"\nProcesando categoría: [{emocion.upper()}]")
            
            for archivo_audio in os.listdir(ruta_emocion):
                if archivo_audio.endswith(('.mp3', '.wav', '.flac')):
                    ruta_completa = os.path.join(ruta_emocion, archivo_audio)
                    
                    # Extraer el vector
                    vector = extraer_caracteristicas_de_audio(ruta_completa)
                    
                    if vector is not None:
                        # Añadimos la etiqueta (nombre de la carpeta) al final del vector
                        fila = list(vector) + [emocion]
                        datos_completos.append(fila)
                        contador +=1
                        porcentaje = (contador / total_archivos) * 100
                        if contador % 10 == 0 or contador == total_archivos:
                            print(f"[{porcentaje:.2f}%] ({contador}/{total_archivos}) Procesado: {archivo_audio}")

    # Guardar todo en un DataFrame de Pandas y exportar a CSV
    df_nuevo = pd.DataFrame(datos_completos, columns=columnas)
    
    # Crear la carpeta de salida si no existe
    os.makedirs(os.path.dirname(ruta_salida_csv), exist_ok=True)
    df_nuevo.to_csv(ruta_salida_csv, index=False)
    
    print(f"\n¡Proceso terminado! Tu nuevo dataset se guardó en: {ruta_salida_csv}")
    print(f"Dimensiones finales del nuevo dataset: {df_nuevo.shape}")

def procesar_y_normalizar_dataset(ruta_csv, ruta_salida_escalado):
    print (f"\nIniciando fase de Normalizacion...")
    print (f"Leyebdo ruta desde: {ruta_csv}")
    df = pd.read_csv(ruta_csv)

    #Separamos las caracteristicas de la etiqueta
    X = df.drop(columns=['label'])
    y = df['label']

    #Aplicando la normalizacion de las caracteristicas con media 0 y varianza de 1
    print ("Aplicando StandardScaler a las 27 caracteristicas...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #Reconstruimos el archivo original
    df_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    df_scaled['label'] = y

    #Guardar cambios del csv
    df_scaled.to_csv(ruta_salida_escalado, index=False)
    print(f"Dataset normalizado guardado con exito en: {ruta_salida_escalado}")
    print(f"Rango Maximo detectado en los datos escalados: {X_scaled.max():.2f}")
    print(f"Rango Minimo detectado en los datos escalados: {X_scaled.min():.2f}")

    return df_scaled

# Ejecución principal
if __name__ == "__main__":
    CARPETA_AUDIOS = "data/raw"
    CSV_CRUDO = "data/processed/mi_music_dataset.csv"
    CSV_ESCALADO = "data/processed/mi_music_dataset_scaled.csv"

    #Validacion
    #Si NO existe el CSV crudo, lee los audios y lo crea
    if not os.path.exists(CSV_CRUDO):
        print(f"Aviso:No se encontro '{CSV_CRUDO}'.\n Iniciando extraccion desde los audios crudos...")
        generar_dataset_csv(CARPETA_AUDIOS, CSV_CRUDO)
    else:
        print (f"Aviso: El archivo '{CSV_CRUDO}' ya existe, solo se normalizara")
    
    #Normalizacion de los datos siempre del CSV ya existente
    df_listo = procesar_y_normalizar_dataset(CSV_CRUDO, CSV_ESCALADO)
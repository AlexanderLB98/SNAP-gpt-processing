# SNAP-gpt-processing
Uses SNAP Graphic Proccesing Tool to analyze images
Este programa se encarga de analizar imágenes utilizando comandos directos de SNAP GPT.

**Requisitos previos**
-------------------

* Python 3.x instalado en el sistema
* Bibliotecas necesarias para el programa instaladas (pandas, etc.)
* Configuración del programa definida en `config.yaml`

# Uso
1. Asegúrate de tener todas las dependencias instaladas.
2. Prepara el archivo de configuración config.yaml según tus necesidades.
3. Ejecuta el programa con el siguiente comando:

``` 
python gpt_snap.py
```

El programa procesará todas las imágenes en la carpeta especificada en image_folder, y guardará los resultados en un archivo CSV llamado results.csv en la misma carpeta que el script.



**Descripción del proceso del programa**
-----------------

1. **Lectura de configuración**
 * El programa lee un archivo de configuración llamado `config.yaml` que contiene los parámetros necesarios para el proceso.
 * Los parámetros incluyen la ruta a la carpeta de entradas (`image_folder`) y la ruta a la carpeta de salidas (`output_folder`)
2. **Iterar sobre las imágenes**
 * El programa itera sobre las imágenes en la carpeta de entradas (`input_folder`).
 * Para cada imagen, se ejecuta el método `process_image()`.
3. **Procesamiento de la imagen**
 * El método `process_image()` verifica si la imagen ya ha sido procesada previamente utilizando el método `check_done()`.
 * Si la imagen no ha sido procesada antes, se procede a realizar los siguientes pasos:
 + Se crea una carpeta específica para la imagen en la carpeta de salidas (`output_folder`).
 + Se llama al método `resample_image()` para remuestrear la imagen.
 + Se llama al método `apply_c2rcc()` para aplicar la corrección atmosférica C2RCC a la imagen remuestreada.
 + Se llama al método `apply_pixex()` para extraer datos del punto de la imagen procesada.
 + Se limpia la carpeta específica para la imagen eliminando los archivos y carpetas innecesarios utilizando el método `clean_folder()`.
 + Se lee los archivos de medida (`_measurements.txt`) en la carpeta específica para la imagen utilizando el método `read_measurement_files()`.
4. **Lectura de archivos de medidas**
 * El método `read_measurement_files()` busca todos los archivos que terminan en `_measurements.txt` en las carpetas específicas para cada imagen y los lee en un DataFrame (`all_data`) utilizando la biblioteca pandas.
 * Se almacena el DataFrame en un archivo CSV llamado `results.csv`.
5. **Finalización del programa**
 * Después de haber procesado todas las imágenes, se ejecuta el método `read_measurement_files()` una vez más para leer todos los archivos de medida y almacenarlos en un único DataFrame (`df_all_images`).
 * Se almacena el DataFrame en un archivo CSV llamado `results.csv`.

**Comandos que se ejecutan de GPT en el programa**
--------------------------------------------

1. **Remuestreo de la imagen**
 * El comando `resample_image()` llama al comando GPT `Resample` con las siguientes opciones:
 + `-PtargetResolution=10`: establece la resolución objetivo del remuestreo.
 + `-t <output_path>`: especifica la ruta de salida para el archivo remuestreado.
 + `<input_file>`: especifica la ruta del archivo de entrada (la imagen original).
```bash
gpt Resample -PtargetResolution=10 -t output/imageX/resampled imageX.dim
```
2. **Aplicación de corrección atmosférica C2RCC**
 * El comando `apply_c2rcc()` llama al comando GPT `c2rcc.msi` con las siguientes opciones:
 + `-SsourceProduct=<source_product>`: especifica el producto de entrada (el archivo remuestreado).
 + `-t <output_directory>`: especifica la ruta de salida para los archivos procesados.
 + `-PnetSet='C2X-Nets'`: establece la red neuronal a utilizar para la corrección atmosférica.
 + `-PoutputAsRrs=true`: especifica que el archivo de salida debe ser un archivo RRS ( Reflectance at Sea Surface).
```bash
gpt c2rcc.msi -SsourceProduct=output/imageX/resampled.dim -t output/imageX/c2rcc.c2rcc -PnetSet='C2X-Nets' -PoutputAsRrs=true
```
3. **Extraer datos del punto**
 * El comando `apply_pixex()` llama al comando GPT `PixEx` con las siguientes opciones:
 + `-PwindowSize=3`: establece el tamaño de la ventana para extraer los datos del punto.
 + `-PcoordinatesFile=<coordinates_file>`: especifica la ruta del archivo de coordenadas.
 + `-PsourceProductPaths=<input_file>`: especifica la ruta del archivo de entrada (el producto procesado anteriormente).
 + `-t <output_directory>`: especifica la ruta de salida para los archivos procesados.
 + `-PoutputFilePrefix=<output_prefix>`: establece el prefijo para el archivo de salida.
```bash
gpt PixEx -PwindowSize=3 -PcoordinatesFile=coordinates.txt -PsourceProductPaths=output/imageX/c2rcc.c2rcc.dim -t output/imageX/pixex -PoutputFilePrefix=pixex_output
```
Estos comandos se ejecutan en secuencia para procesar cada imagen y extraer los datos del punto.
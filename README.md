# Conteo de multitudes (Crowd Counting)

Este repositorio contiene el código empleado en el proyecto de tesis acerca del conteo de múltitudes den imagen a través de aprendizaje profundo, para la Facultad de Ingeniería (FING) de la Universidad de la República del Uruguay (Udelar).

El mismo adjunta un archivo `requirements.txt` con las bibliotecas de Python empleadas durante la elaboración de los entregables.

El mismo se divide en cuatro directorios:

## cclabeler-mt-renzo

Contiene el código de [CCLabeler](https://github.com/Elin24/cclabeler) empleado por el estudiante para la anotación de imagenes en el módulo de taller.

Se hayan en el las anotaciones del estudiante e imagenes del modulo de taller. Tras instalar `requirements.txt`

Se puede correr con `python manage.py runserver 0.0.0.0:8000` y accediendo a [http://localhost:8000](http://localhost:8000) con el usuario `mtcrowd` y contraseña `mtcrowd`.

## conjunto-datos-mt

Este directorio contiene:
- El conjunto de datos MT en la carpeta `images`.
- Sus 12 anotaciones para cada imagen en la carpeta `ground truth`.
- La divisón en cuatro subconjuntos en la carpeta `images_split`.
- El script `mtcc.py` basado en las dependencias del [requirements.txt](https://github.com/renzodgc/fing-crowdcounting/blob/main/requirements.txt) del repositorio general. Que analiza los datos y genera las graficas y tablas entregadas.
- Las gráficas generadas y métricas obtenidas y empleadas en el informe se encuentran en la ccarpeta `graphs` y `metrics`.

El script `mtcc.py` genera los siguientes resultados:
- Lee las anotaciones del conjunto en su totalidad y sus subconjuntos a través de la función `read_annotations`.
- La función `visualize_annotations` es aplicada a cada subconjunto de datos, la misma calcula la media y desviación estandar de cada imagen, e imprime en consola texto cuyo formato es inyectable en Latex para las tablas del informe, marcando los valores atípicos en negrita.
- La función `box_plot` grafica el diagrama de caja para las anotaciones de cada imagen en cada subconjunto, marcando su media, mediana, cuartiles y valores atípicos.
- La función `print_general_statistics` imprime la media en total entre todas las anotaciones para todas las imagenes.
- La función `process_metrics` usa los archivos generales `results_models_count.csv` y `results_models_metrics.json` (generados con el código de [experimentacion con modelos](https://github.com/renzodgc/fing-crowdcounting/tree/main/experimentacion-modelos)), y divide las metricas evaluadas para los modelos de la experimentación y la totalidad del conjunto **entre los cuatro subconjuntos de evaluación** (baja, media, paraguas, aéreo).

## experimentacion-modelos

Este directorio contiene:
- Dentro de la carpeta `resultados` se encuentran los resultados obtenidos durante la experimentación evaluando con distintos modelos, así como scripts usados para corregir o combinar los mismos.
- El `notebook` `CC-Evaluation.ipynb`, el cual se ejecutó a través de [Google Collab](https://colab.research.google.com/).

El mismo se puede correr localmente modificandolo levemente para leer los archivos desde un directorio y no desde un [Google Drive](https://drive.google.com). Se menciona sin embargo que el modelo SASNet, obtenido de su [implementacion oficial](https://github.com/TencentYoutuResearch/CrowdCounting-SASNet) consume bastantes RAM al correr en CPU, y VRAM al correr en GPU.

Para correr el mismo en [Google Collab](https://colab.research.google.com/) es necesario crear en la carpeta `Colab Notebooks` los siguientes directorios:
- `Models/SASNet` y en el colocar:
    - Los archivos de [la implementacion oficial de SASNet](https://github.com/TencentYoutuResearch/CrowdCounting-SASNet)
    - La carpeta `checkpoints` que contenga los pesos para el modelo entrenado con SHA y SHB obtenidos del [Drive de la implementación oficial](https://drive.google.com/drive/folders/1uTkJLQOn-jQg81yNAluBpGpIJ-XaZaGI)
- `Datasets`, que debe contener los siguientes directorios:
    - `UCF_CC`: Conteniendo las carpetas `images` y `ground_truth`, separando las imagenes `.jpg` y anotaciones `.mat` del [conjunto de datos](https://www.crcv.ucf.edu/data/ucf-cc-50/).
    - `UCF-QNRF_ECCV18/Test`: Conteniendo las carpetas `images` y `ground_truth`, separando las imagenes `.jpg` y anotaciones `.mat` del [conjunto de datos de Test](https://www.crcv.ucf.edu/data/ucf-qnrf/).
    - `MT`: Conteniendo las carpetas `images` y `ground_truth`, la primera conteniendo la totalidad de imagenes `.jpg` y la segunda contieniendo **un solo conjunto de anotaciones** `.json` del [conjunto de datos MT](https://github.com/renzodgc/fing-crowdcounting/tree/main/conjunto-datos-mt).
    - `Shanghaitech/part_A_final/test_data`: Conteniendo las carpetas `images` y `ground_truth`, separando las imagenes `.jpg` y anotaciones `.mat` del [conjunto de datos SHA de Test](https://drive.google.com/file/d/1DLgEpNEPp3UqPnEtzW0BSMdS151kRNCs/view?usp=share_link).
    - `Shanghaitech/part_B_final/test_data`: Conteniendo las carpetas `images` y `ground_truth`, separando las imagenes `.jpg` y anotaciones `.mat` del [conjunto de datos SHB de Test](https://drive.google.com/file/d/1DLgEpNEPp3UqPnEtzW0BSMdS151kRNCs/view?usp=share_link).

El script `mtcc.py` genera los siguientes resultados, imprimiendolos en consola:
- Métricas de evaluación en promedio para cada conjunto de datos, evaluado con cada uno de los modelos
    - Se destaca como la métrica RMSE se genera de manera erronea y el arreglo de la misma se haya en el archivo auxiliar `resultados/fix_rmse`.
- Capacidad de correr [SASNet](https://github.com/TencentYoutuResearch/CrowdCounting-SASNet) con CPU o GPU
- Generar para una evaluación de modelo, pesos y conjunto N imagenes con sus métricas individuales.
    - Destacar que se generan por separado para los modelos de [LWCC](https://github.com/tersekmatija/lwcc) y los de [SASNet](https://github.com/TencentYoutuResearch/CrowdCounting-SASNet).

Los scripts auxiliares dentro de la carpeta `resultados` son:
- `average_results`: Promedia los resultados para múltiples corridas de SHB y QNRF, que por restricciones de recursos en Colab se tuvo que correrlos en dos ejecuciones, partiendo los conjuntos de datos.
- `fix_rmse`: Arregla la métrica RMSE, que en el notebook de experimentación se calcula de manera incorrecta.
- `image_merger`: Combina las imagenes de anotación generadas por los modelos de [LWCC](https://github.com/tersekmatija/lwcc) y los de [SASNet](https://github.com/TencentYoutuResearch/CrowdCounting-SASNet).

## imagenes-informe

Contiene la gran mayoría de imagenes empleadas en el informe entregado.

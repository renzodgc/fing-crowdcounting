Este repositorio contiene el código empleado en el proyecto de tesis acerca del conteo de múltitudes den imagen a través de aprendizaje profundo, para la Facultad de Ingeniería (FING) de la Universidad de la República del Uruguay (Udelar).

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

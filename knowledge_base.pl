% knowledge_base.pl
% Base de conocimiento para selección de prueba estadística

:- encoding(utf8). % Añadido para manejar tildes y caracteres especiales

:- dynamic respuesta/2. % Predicado dinámico para almacenar las respuestas del usuario

% Preguntas al usuario con identificador (los IDs son simbólicos ahora)
pregunta(objetivo, '¿Cuál es el objetivo de tu estudio?', [comparar_medias, comparar_proporciones, evaluar_asociacion, evaluar_relacion_lineal, predecir_variable]).
pregunta(tipo_variable, '¿Qué tipo de variable es tu dependiente (o la principal de interés)?', [numerica, categorica]).
pregunta(numero_grupos, '¿Cuántos grupos están involucrados en la comparación (si aplica)?', [uno, dos, mas_de_dos, n_a]).
pregunta(relacion_grupos, '¿Tus muestras/mediciones son independientes o pareadas (si aplica)?', [independientes, pareadas, n_a]).
pregunta(normalidad, '¿Tus datos (o los residuos del modelo) siguen una distribución normal?', [si, no, no_se, n_a]). % Añadida 'no_se'
pregunta(varianzas_iguales, '¿Tus grupos tienen varianzas iguales (homogéneas)?', [si, no, no_se, n_a]). % Añadida 'no_se'
pregunta(tipo_comparacion_proporcion, '¿Se compara una proporción esperada (respecto a un valor fijo) o entre grupos?', [esperada, entre_grupos, n_a]). % Nueva pregunta para proporciones
pregunta(tipo_vd_categorica_prediccion, '¿La variable dependiente categórica es dicotómica (2 categorías) o multinomial (>2 categorías)?', [dicotomica, multinomial, n_a]). % Nueva pregunta para predicción categórica

% Reglas para selección de pruebas estadísticas - ¡Basadas DIRECTAMENTE en cada fila de la tabla!

% Fila 1: Comparar medias (Numérica, 1, N/A, Sí, N/A) -> t de Student una muestra
seleccionar_prueba(t_test_una_muestra) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, uno),
    respuesta(normalidad, si).

% Fila 2: Comparar medias (Numérica, 2, Independientes, Sí, Sí) -> t de Student independiente
seleccionar_prueba(t_test_independiente) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, dos),
    respuesta(relacion_grupos, independientes),
    respuesta(normalidad, si),
    respuesta(varianzas_iguales, si).

% Fila 3: Comparar medias (Numérica, 2, Independientes, No, N/A) -> Mann-Whitney U
seleccionar_prueba(mann_whitney_u) :- % Renombrado
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, dos),
    respuesta(relacion_grupos, independientes),
    respuesta(normalidad, no).

% Fila 4: Comparar medias (Numérica, 2, Pareadas, Sí, N/A) -> t de Student pareada
seleccionar_prueba(t_test_pareada) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, dos),
    respuesta(relacion_grupos, pareadas),
    respuesta(normalidad, si).

% Fila 5: Comparar medias (Numérica, 2, Pareadas, No, N/A) -> Wilcoxon pareada
seleccionar_prueba(wilcoxon_pareada) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, dos),
    respuesta(relacion_grupos, pareadas),
    respuesta(normalidad, no).

% Fila 6: Comparar medias (Numérica, >2, Independientes, Sí, Sí) -> ANOVA
seleccionar_prueba(anova) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, mas_de_dos),
    respuesta(relacion_grupos, independientes),
    respuesta(normalidad, si),
    respuesta(varianzas_iguales, si).

% Fila 7: Comparar medias (Numérica, >2, Independientes, No, N/A) -> Kruskal-Wallis
seleccionar_prueba(kruskal_wallis) :-
    respuesta(objetivo, comparar_medias),
    respuesta(tipo_variable, numerica),
    respuesta(numero_grupos, mas_de_dos),
    respuesta(relacion_grupos, independientes),
    respuesta(normalidad, no).

% Fila 8: Comparar proporciones (Categórica, 1 o más, N/A, N/A, N/A, Esperada) -> Chi-cuadrado (Bondad de Ajuste)
seleccionar_prueba(chi_cuadrado_bondad_ajuste) :-
    respuesta(objetivo, comparar_proporciones),
    respuesta(tipo_variable, categorica),
    respuesta(tipo_comparacion_proporcion, esperada).

% Fila 9: Comparar proporciones (Categórica, 1 o más, N/A, N/A, N/A, Entre grupos) -> Chi-cuadrado (Independencia)
seleccionar_prueba(chi_cuadrado_independencia) :-
    respuesta(objetivo, comparar_proporciones),
    respuesta(tipo_variable, categorica),
    respuesta(tipo_comparacion_proporcion, entre_grupos).

% Fila 10: Evaluar asociación (Categórica, 2 variables, Independientes, N/A, N/A) -> Chi-cuadrado de independencia
seleccionar_prueba(chi_cuadrado_independencia) :- % Puede ser la misma prueba para otro objetivo
    respuesta(objetivo, evaluar_asociacion),
    respuesta(tipo_variable, categorica),
    respuesta(numero_grupos, dos). % Aunque la tabla dice "2 variables", para asociación de categóricas, se refiere a la relación entre ellas, no grupos.
                                   % Si hablamos de asociación entre dos variables, el contexto de "grupos" puede ser ambiguo.
                                   % Aquí asumo que "2 variables" se refiere a la interacción entre dos variables categóricas, donde cada una define "grupos" o categorías.
                                   % La condición "Independientes" se aplica a las observaciones, no a las variables en sí.
                                   % Para la asociación de dos variables categóricas, no se pregunta por el número de grupos. Quitaremos numero_grupos y relacion_grupos.

% Re-evaluación para Evaluar Asociación (Fila 10):
% La tabla indica "2 variables" y "Independientes". Esto se refiere a dos variables categóricas
% y que las observaciones son independientes entre sí, no que haya "grupos" como en comparar medias.
% Ajustaremos la regla para que sea más directa:
seleccionar_prueba(chi_cuadrado_independencia_asociacion) :- % Renombrado para diferenciar de la de proporciones
    respuesta(objetivo, evaluar_asociacion),
    respuesta(tipo_variable, categorica). % Implica que son dos variables categóricas para evaluar asociación

% Fila 11: Evaluar relación lineal (Numérica (ambas), N/A, N/A, Sí, N/A) -> Correlación de Pearson
seleccionar_prueba(correlacion_pearson) :-
    respuesta(objetivo, evaluar_relacion_lineal),
    respuesta(tipo_variable, numerica), % Implica que ambas variables son numéricas
    respuesta(normalidad, si).

% Fila 12: Evaluar relación lineal (Numérica (ambas), N/A, N/A, No, N/A) -> Correlación de Spearman
seleccionar_prueba(correlacion_spearman) :-
    respuesta(objetivo, evaluar_relacion_lineal),
    respuesta(tipo_variable, numerica), % Implica que ambas variables son numéricas
    respuesta(normalidad, no).

% Fila 13: Predecir variable (Numérica, N/A, N/A, Sí, N/A) -> Regresión Lineal
seleccionar_prueba(regresion_lineal) :-
    respuesta(objetivo, predecir_variable),
    respuesta(tipo_variable, numerica),
    respuesta(normalidad, si).

% Fila 14: Predecir variable (Categórica, N/A, N/A, N/A, N/A, N/A, Dicotómica) -> Regresión Logística Binaria
seleccionar_prueba(regresion_logistica_binaria) :-
    respuesta(objetivo, predecir_variable),
    respuesta(tipo_variable, categorica),
    respuesta(tipo_vd_categorica_prediccion, dicotomica).

% Fila 15: Predecir variable (Categórica, N/A, N/A, N/A, N/A, N/A, Multinomial) -> Regresión Logística Multinomial
seleccionar_prueba(regresion_logistica_multinomial) :-
    respuesta(objetivo, predecir_variable),
    respuesta(tipo_variable, categorica),
    respuesta(tipo_vd_categorica_prediccion, multinomial).

% Regla por defecto si no se encuentra ninguna prueba
seleccionar_prueba(no_recomendada).

% Explicaciones de las pruebas
explicacion_prueba(t_test_una_muestra, 'La prueba t de Student para una muestra se utiliza para comparar la media de una única muestra numérica con un valor poblacional conocido cuando los datos son normales.').
explicacion_prueba(t_test_independiente, 'La prueba t de Student para muestras independientes se utiliza para comparar las medias de dos grupos distintos cuando los datos son numéricos y siguen una distribución normal, los grupos son independientes y las varianzas son homogéneas.').
explicacion_prueba(mann_whitney_u, 'La prueba U de Mann-Whitney (equivalente no paramétrico de la t-test independiente) compara las medianas de dos grupos independientes cuando los datos son numéricos y no siguen una distribución normal.').
explicacion_prueba(t_test_pareada, 'La prueba t pareada se usa para comparar dos mediciones relacionadas (ej. antes y después) en el mismo grupo con datos numéricos que siguen una distribución normal.').
explicacion_prueba(wilcoxon_pareada, 'La prueba de Wilcoxon (equivalente no paramétrico de la t-test pareada) se usa para comparar dos mediciones relacionadas (antes/después) cuando los datos son numéricos y no siguen una distribución normal.').
explicacion_prueba(anova, 'El ANOVA de un factor (Análisis de Varianza) compara las medias de más de dos grupos independientes cuando los datos son numéricos, siguen una distribución normal y las varianzas son homogéneas.').
explicacion_prueba(kruskal_wallis, 'La prueba de Kruskal-Wallis (equivalente no paramétrico del ANOVA) compara las medianas de más de dos grupos independientes cuando los datos son numéricos y no siguen una distribución normal.').
explicacion_prueba(chi_cuadrado_bondad_ajuste, 'La prueba Chi-cuadrado de bondad de ajuste se utiliza para comparar las frecuencias observadas de una sola variable categórica con las frecuencias esperadas, para determinar si se ajustan a una distribución teórica.').
explicacion_prueba(chi_cuadrado_independencia, 'La prueba Chi-cuadrado de independencia se utiliza para evaluar si existe una asociación significativa entre dos variables categóricas.').
explicacion_prueba(chi_cuadrado_independencia_asociacion, 'La prueba Chi-cuadrado de independencia es la más común para evaluar la asociación entre dos variables categóricas, determinando si están relacionadas o son independientes.'). % Explicación dedicada para asociación
explicacion_prueba(correlacion_pearson, 'El coeficiente de correlación de Pearson mide la fuerza y dirección de la relación lineal entre dos variables numéricas que siguen una distribución normal.').
explicacion_prueba(correlacion_spearman, 'El coeficiente de correlación de Spearman evalúa la fuerza y dirección de la relación monótona (no necesariamente lineal) entre dos variables numéricas que no siguen una distribución normal.').
explicacion_prueba(regresion_lineal, 'La regresión lineal simple o múltiple analiza cómo una variable numérica dependiente puede ser predicha por una o más variables independientes, asumiendo una relación lineal y normalidad en los residuos.').
explicacion_prueba(regresion_logistica_binaria, 'La regresión logística binaria se utiliza cuando la variable dependiente es categórica y dicotómica (dos categorías), para predecir la probabilidad de que ocurra un evento basándose en una o más variables independientes.').
explicacion_prueba(regresion_logistica_multinomial, 'La regresión logística multinomial se utiliza cuando la variable dependiente es categórica y tiene más de dos categorías (multinomial), para predecir la probabilidad de pertenecer a cada categoría basándose en una o más variables independientes.').
explicacion_prueba(no_recomendada, 'Con la información proporcionada, no se pudo determinar una prueba estadística adecuada. Por favor, revise sus respuestas o consulte a un experto.').

% Limpiar respuestas para reinicio
reiniciar :- retractall(respuesta(_, _)).

% Permite consultar solo el Id y el Texto de las preguntas (usado por el sistema experto en Python)
pregunta(Id, Texto) :- pregunta(Id, Texto, _).
# co-retweeters

Detección de **co-retweeters** en Twitter/X: perfiles que coinciden al retuitear los mismos mensajes muchas más veces de lo esperable. Que dos personas no coordinadas coincidan en cientos de retweets es poco probable, y que ocurra con cientos de perfiles puede indicar difusión coordinada.

El análisis combina Python, para el cálculo pesado de las coincidencias, y R, para el análisis de redes y el informe.

## Estructura

```
co-retweeters/
├── data/                       # Datos (no incluidos)
├── scripts/co-retweeters.py    # Filtrado de retweets y cálculo de coincidencias
└── notebooks/
    ├── co-retweeters.Rmd       # Informe: KPIs, comunidades, tablas y grafos
    ├── config.example.yml      # Plantilla de la configuración local
    └── utils/net.R             # Funciones de grafos (ForceAtlas2)
```

## Cómo funciona

1. **Filtrado** (`get_RTs`, Python):
   - Lee los retweets y quita los duplicados.
   - Descarta los tweets con menos de `min_retweets_msg` o más de `max_retweets_msg` retweets.
   - Descarta a los usuarios con menos de `min_shared_tweets` retweets, porque no pueden llegar a ese número de coincidencias con nadie.
2. **Coincidencias** (`calcular_cocurrencias`, Python): para cada pareja de usuarios cuenta cuántos tweets han retuiteado los dos, y guarda las parejas con al menos `min_shared_tweets` coincidencias.
3. **Informe** (R Markdown):
   - Construye el grafo de co-retweeters, con el número de coincidencias como peso.
   - Detecta comunidades con Leiden.
   - Presenta, para cada comunidad:
     - los KPIs, la amplificación y la distribución;
     - los co-retweeters y las parejas más destacados;
     - el grafo de relaciones y el grafo de beneficiarios (las cuentas retuiteadas).

## Requisitos

- **R** con los paquetes: tidyverse, glue, igraph, ggraph, tidygraph, [ForceAtlas2](https://github.com/analyxcompany/ForceAtlas2), kableExtra, ggtext, stRoke, RColorBrewer, colorspace, reticulate y rmarkdown. El Rmd instala los que falten.
- **Python 3** con `pandas` y `tqdm`, instalado de forma normal o en un entorno conda.

## Uso

1. Copia los datos en `data/<dataset>/<prefix>_RTs.csv`. El fichero necesita las columnas `username` (quien retuitea) y `url_rt` (URL del tweet retuiteado). Opcionalmente, `user_retweeted` (usuario retuiteado) se usa si no se puede sacar de la URL.
2. Rellena los `params` de la cabecera de `notebooks/co-retweeters.Rmd`:
   - `dataset_name` y `prefix`;
   - `author`, tu firma al pie de los gráficos;
   - cómo ejecutar Python: `python_mode: "conda"` con `conda_env`, o `python_mode: "python"` con `python_path` (vacío = el `python` del PATH).
3. Opcional, si usas el cuaderno en varios ordenadores: copia `notebooks/config.example.yml` como `notebooks/config.local.yml` y pon en su bloque `equipos` los valores de cada uno, por ejemplo la ruta de Python. La clave es `Sys.info()[["nodename"]]`, y esos valores sustituyen a los de la cabecera. `config.local.yml` no se sube al repositorio.
4. Abre `co-retweeters.Rproj` en RStudio y haz *Knit* de `notebooks/co-retweeters.Rmd`.

### Subir cambios sin datos personales

`.gitattributes` aplica al Rmd el filtro `params-limpios` (`scripts/limpiar-params.sed`): al hacer commit, la cabecera se guarda con los valores genéricos de dataset, autor y rutas de Python, y tu copia de trabajo no cambia. Para activarlo en tu clon:

```bash
git config filter.params-limpios.clean "sed -E -f scripts/limpiar-params.sed"
git config filter.params-limpios.required true
```

También se puede calcular solo las coincidencias desde la línea de comandos (desde `scripts/`):

```bash
python co-retweeters.py --dataset <dataset> --prefix <prefix> --min_RTs 50 --min_cocurrencias 50
```

## Parámetros del análisis

| Parámetro | Por defecto | Uso |
|---|---|---|
| `min_retweets_msg` | 50 | Mínimo de retweets de un tweet para analizarlo |
| `max_retweets_msg` | 100000 | Máximo de retweets de un tweet para analizarlo |
| `min_shared_tweets` | 50 | Mínimo de coincidencias para considerar co-retweeters a dos perfiles |
| `seed` | 1234 | Semilla para que las comunidades sean reproducibles |
| `author` | | Firma de los gráficos |
| `color` | | Color de la comunidad cuando solo hay un beneficiario |

Los grafos de relaciones y de beneficiarios muestran, en cada comunidad, como máximo los 50 perfiles con más grado (constantes `nodos_grafo_co_retweeters` y `nodos_grafo_beneficiarios` del chunk `environment`).

El ajuste de los umbrales es empírico y depende de cada dataset. Si no hay parejas que superen `min_shared_tweets`, el informe se detiene con un aviso.

## Autora

Mariluz Congosto ([@congosto](https://twitter.com/congosto))

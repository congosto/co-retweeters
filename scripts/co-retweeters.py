# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:46:41 2026

@author: Congosto

Detección de co-retweeters.

Se puede usar de dos formas:
  - Desde R con reticulate::source_python() (notebooks/co-retweeters.Rmd),
    que carga las funciones get_RTs() y calcular_cocurrencias().
  - Desde línea de comandos:
      python co-retweeters.py --dataset papeles_cni --prefix ceuta_cni
"""

# import modules
import pandas as pd
import os
import sys
import csv
from tqdm import tqdm
import time
from datetime import timedelta
from collections import defaultdict
import argparse


def calcular_KPIs(retweets):
  # Métricas básicas de un dataframe de retweets
  return {
    "n_tweets": int(retweets["target"].nunique()),
    "n_retweeters": int(retweets["origin"].nunique()),
    "n_RTs": int(len(retweets)),
    "n_beneficiarios": int(retweets["user_target"].nunique())
  }


def contar(serie, nombre):
  # Convierte un value_counts en dataframe de dos columnas (nombre, count)
  df = serie.value_counts().rename_axis(nombre).reset_index(name="count")
  df["count"] = df["count"].astype(int)
  return df


def get_RTs(base_path, prefix, min_RTs, max_RTs, min_cocurrencias):

  RTs_file = os.path.join(base_path, f'{prefix}_RTs.csv')
  # Leer CSV
  retweets = (
    pd.read_csv(RTs_file, dtype=str)
      # Quitamos repetidos por username + url_rt
      .drop_duplicates(subset=["username", "url_rt"])
      # Renombrar columnas
      .rename(columns={
        "username": "origin",
        "url_rt": "url"
        })
  )
  # Crear columna target extrayendo lo que va después de "status/"
  retweets["target"] = retweets["url"].str.replace(r".*status/", "", regex=True)
  # Usuario retuiteado: se extrae de la URL y, si no se puede, de user_retweeted
  retweets["user_target"] = retweets["url"].str.extract(
    r"(?:twitter|x)\.com/([^/]+)/status",
    expand=False
   )
  if "user_retweeted" in retweets.columns:
    retweets["user_target"] = retweets["user_target"].fillna(retweets["user_retweeted"])
  # Seleccionar columnas finales
  retweets = retweets[["origin", "target", "user_target"]].dropna(subset=["origin", "target"])

  KPIs_raw = calcular_KPIs(retweets)
  # RTs recibidos por cada beneficiario en el dataset completo
  users_target_count = contar(retweets["user_target"], "user_target")

  # 1. Filtrar targets por min_RTs y max_RTs (ambos incluidos)
  targets_count = retweets["target"].value_counts()
  valid_targets = targets_count[
    (targets_count >= min_RTs) &
    (targets_count <= max_RTs)
   ].index
  retweets = retweets[retweets["target"].isin(valid_targets)]

  # 2. Filtrar origins: quien ha hecho menos de min_cocurrencias RTs
  #    no puede coincidir min_cocurrencias veces con nadie
  origins_count = retweets["origin"].value_counts()
  valid_origins = origins_count[origins_count >= min_cocurrencias].index
  retweets = retweets[retweets["origin"].isin(valid_origins)].reset_index(drop=True)

  KPIs_filtered = calcular_KPIs(retweets)
  # RTs hechos por cada retweeter dentro del dataset filtrado
  origins_count = contar(retweets["origin"], "origin")

  return {
    "retweets": retweets,
    "origins_count": origins_count,
    "users_target_count": users_target_count,
    "KPIs_raw": KPIs_raw,
    "KPIs_filtered": KPIs_filtered
  }


def calcular_cocurrencias(retweets, file_cocurrencias, min_cocurrencias):

  min_cocurrencias = int(min_cocurrencias)
  # Crear indices inversos
  # dict_targets: target → [origins]
  dict_targets = retweets.groupby("target")["origin"].agg(list).to_dict()
  # dict_origins: origin → [targets]
  dict_origins = retweets.groupby("origin")["target"].agg(list).to_dict()

  n_parejas = 0
  procesados = set()
  with open(file_cocurrencias, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["usuario_1", "usuario_2", "cocurrencias"])
    # tqdm envuelve el dict de origins para mostrar progreso
    for origin, targets in tqdm(dict_origins.items(), desc="Procesando origins"):
      cocurrencias = defaultdict(int)
      for target in targets:
        for u in dict_targets.get(target, []):
          # Evitar emparejar consigo mismo y las parejas ya contadas
          # cuando u se procesó como origin
          if u == origin or u in procesados:
            continue
          cocurrencias[u] += 1

      # Marcamos este origin como procesado
      procesados.add(origin)
      # Filtrar por mínimo de cocurrencias y guardar
      for u, count in cocurrencias.items():
        if count >= min_cocurrencias:
          u1, u2 = sorted((origin, u))
          writer.writerow([u1, u2, count])
          n_parejas += 1

  return n_parejas


def main():
  parser = argparse.ArgumentParser(description='Detección de co-retweeters.')
  parser.add_argument('--dataset', type=str, required=True, help='Directorio del dataset dentro de --data.')
  parser.add_argument('--prefix', type=str, required=True, help='Prefijo de los ficheros del dataset.')
  parser.add_argument('--data', type=str, required=False, default='../data', help='Directorio raíz de los datos.')
  parser.add_argument('--min_RTs', type=int, required=False, default=10, help='Mínimo de RTs de un tweet para analizarlo.')
  parser.add_argument('--max_RTs', type=int, required=False, default=5000, help='Máximo de RTs de un tweet para analizarlo.')
  parser.add_argument('--min_cocurrencias', type=int, required=False, default=50, help='Mínimo de coincidencias entre dos usuarios.')
  args = parser.parse_args()

  base_path = os.path.join(args.data, args.dataset)
  RTs_file = os.path.join(base_path, f'{args.prefix}_RTs.csv')
  cocurrencias_file = os.path.join(base_path, f'{args.prefix}_co_retweets.csv')

  if not os.path.exists(RTs_file):
    print(f'{RTs_file} does not exist')
    sys.exit(1)

  inicio = time.perf_counter()
  res = get_RTs(base_path, args.prefix, args.min_RTs, args.max_RTs, args.min_cocurrencias)
  print(f'KPIs originales: {res["KPIs_raw"]}')
  print(f'KPIs filtrados:  {res["KPIs_filtered"]}')

  n_parejas = calcular_cocurrencias(res["retweets"], cocurrencias_file, args.min_cocurrencias)
  print(f'parejas de co-retweeters: {n_parejas} -> {cocurrencias_file}')

  fin = time.perf_counter()
  print(f"Tiempo de ejecución: {timedelta(seconds=fin - inicio)}")


# reticulate::source_python() también ejecuta el script como __main__,
# así que main() solo se lanza si no se ha cargado desde R (rpytools es de reticulate)
if __name__ == "__main__" and "rpytools" not in sys.modules:
  main()

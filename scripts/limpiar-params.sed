# Filtro "clean" de git para notebooks/co-retweeters.Rmd (ver .gitattributes).
# Al hacer commit deja genéricos los parámetros personales de la cabecera YAML.
# La copia de trabajo no cambia. Solo actúa entre el primer y el segundo "---".
1,/^---\r?$/ {
  s/^( +dataset_name: *)"[^"]*"/\1"mi_dataset"/
  s/^( +prefix: *)"[^"]*"/\1"mi_dataset"/
  s/^( +author: *)"[^"]*"/\1""/
  s/^( +python_mode: *)"[^"]*"/\1"python"/
  s/^( +python_path: *)"[^"]*"/\1""/
  s/^( +conda_env: *)"[^"]*"/\1"reticulate"/
  s/^( +conda_path: *)"[^"]*"/\1""/
}

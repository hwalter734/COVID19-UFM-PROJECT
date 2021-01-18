library(readr)
library(dplyr)
library(tidyr)

df <- read_csv('casos_municipios.csv')
df <- df %>%
  pivot_longer(!c(departamento,codigo_departamento,municipio,codigo_municipio,poblacion), 
               names_to = "Fecha", values_to = "count")
df <- filter(df, municipio == 'GUATEMALA')

write_csv(df, 'casos_guatemala.csv')

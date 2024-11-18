import csv
import json


# Lista para armazenar os dados do CSV
data = []

# Abrir o arquivo CSV e ler seu conteúdo
with open("data/nomes_brasileiros.csv", mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    # Cada linha do CSV é adicionada como um dicionário à lista de dados
    for row in csv_reader:
        data.append(f"[{row['Nome'].capitalize()}](PERSON)")

with open("datasets/nomes_brasileiros.json", mode="w", encoding="utf-8") as json_file:
    json.dump(data, json_file)

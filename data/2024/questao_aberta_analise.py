import pandas as pd

# Caminho para o arquivo CSV

for arquivo_csv in [ "Servidores_dados_2024.csv", "Estudantes_dados_2024.csv"]:
    
        
    # Lê o arquivo CSV em um DataFrame
    df = pd.read_csv(arquivo_csv, sep=';')
    
    # Seleciona a última coluna
    ultima_coluna = df.iloc[:, -1]
    
    # Conta o número de entradas não vazias na última coluna
    numero_entradas_nao_vazias = ultima_coluna.notna().sum()
    perfil=arquivo_csv.split('_')[0]
    
    # Exibe o resultado
    print(f"Número de respostas para o perfil {perfil`}: {numero_entradas_nao_vazias}")
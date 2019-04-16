import csv
from google.cloud import datastore
from datetime import datetime
from pytz import timezone

#http://www.anbima.com.br/feriados/feriados.asp

with open('feriados.csv', 'r') as ficheiro:

    reader = csv.reader(ficheiro, delimiter=';')
    ds = datastore.Client()
    
    for linha in reader:

        data = datetime.strptime(linha[0], "%d/%m/%Y").replace(tzinfo=timezone('America/Sao_Paulo'))
        id = int(datetime.strftime(data, "%Y%m%d"))
        key = ds.key("Feriados", id)
        #dados = {"id": id, "data": data, "descricao": linha[2]}
        dados = {"id": id, "int_dt_feriado": id, "descricao": linha[2]}

        entity = datastore.Entity(key=key)
        entity.update(dados)
        ds.put(entity)
        
        print (linha)
        


        

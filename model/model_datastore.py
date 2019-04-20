# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Importanto web framework Flask
from flask import current_app
# Importa o cliente Google Cloud Datasotore
from google.cloud import datastore
# Importa classe para Enumeradores
from enum import Enum
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext

builtin_list = list

class TipoEntidade(Enum):
    ''' Enum que define os tipos das entidades do banco de dados
    '''
    INDEXADORES = 'Indexadores'
    INDICES = 'Indices'
    FERIADOS = 'Feriados'

def init_app(app):
    pass

def get_client():
    # return datastore.Client(current_app.config['PROJECT_ID'])
    return datastore.Client()

def list_indexadores(dt_referencia :datetime=None):
    # Instancia o cliente do banco de dados NOSQL GCloud DataStore
    ds = get_client()
    # Prepara a query para consultar valores do índice IPCA
    query = ds.query(kind=TipoEntidade.INDEXADORES.value)
    # Inclui filtros da consulta caso passados
    if dt_referencia is not None:
        query.add_filter('dt_ult_referencia','<', dt_referencia.isoformat())
    #Define ordenação da consulta
    query.order = ['dt_ult_referencia']
    # Executa a consulta e armazena num dictionary 
    #lista = list(query.fetch())
    lista = query.fetch()

    entities = builtin_list(map(from_datastore, lista))
    
    return entities

def list_indices(indexador :str, dataInicial :datetime, dataFinal : datetime):
    # Instancia o cliente do banco de dados NOSQL GCloud DataStore
    ds = get_client()
    # Prepara a query para consultar valores do índice IPCA
    query = ds.query(kind=TipoEntidade.INDICES.value)
    # Inclui filtros da consulta
    query.add_filter('tp_indice','=',indexador)
    query.add_filter('dt_referencia','>=', dataInicial.isoformat())
    query.add_filter('dt_referencia','<=', dataFinal.isoformat())
    #Define ordenação da consulta
    query.order = ['dt_referencia']
    # Executa a consulta e armazena num dictionary 
    indices = list(query.fetch())
    # TODO: Veificar se é necessário utilizar o método from_datastore()
    print(indices)
    # Trata os formatos retornados da lista de entidades
    indices = list(map(lambda e: _tratar_formatos(e), indices))
    print(indices)
    return indices

# def insert_indices():
#      # Obtém uma chave para inclusão do novo índice
#     chave_indice = datastore_client.key('Indices')
#     # Prepara a nova entidade instanciando-a 
#     indice = datastore.Entity(key=chave_indice)
#     # Define o valor da(s) propriedade(s) da entidade
#     indice['dt_referencia'] = ano_mes
#     indice['val_indice'] = val_indice
#     # Insere o novo índice
#     datastore_client.put(indice)

def from_datastore(entity: datastore.Entity):
    """Converte os resultados do Google Datastore no formato esperado (dictionary).
    Exemplo:
    Datastore tipicamente retorna:
        [Entity{key: (kind, id), prop: val, ...}]

    Este método retornará:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.name
    entity = _tratar_formatos(entity)

    return entity

def read(kind: TipoEntidade, id: str):
    ds = get_client()
    key = ds.key(kind.value, id)
    results = ds.get(key)
    return from_datastore(results)

def update(kind: TipoEntidade, data: list, id: str = None):
    ds = get_client()
    if id:
        key = ds.key(kind.value, id)
    else:
        key = ds.key(kind.value)

    # entity = datastore.Entity(
    #     key=key) ,
    #     exclude_from_indexes=['description'])
        
    entity = datastore.Entity(key=key)

    entity.update(data)
    ds.put(entity)
    
    #return from_datastore(entity)
    return key

create = update

def delete(kind: TipoEntidade, id: str):
    ds = get_client()
    key = ds.key(kind.value, id)
    ds.delete(key)
    return key

def update_multi(kind: TipoEntidade, lista: list):
    ds = get_client()
    entities = []
    for item in lista:
        key = ds.key(kind.value, item['id'])
        entity = datastore.Entity(key=key)
        entity.update(item)
        entities.append(entity)
    
    ds.put_multi(entities)
    
    #return from_datastore(entity)
    return


# Lista com paginação
# def list(limit=10, cursor=None):
#     ds = get_client()

#     query = ds.query(kind='Book', order=['title'])
#     query_iterator = query.fetch(limit=limit, start_cursor=cursor)
#     page = next(query_iterator.pages)

#     entities = builtin_list(map(from_datastore, page))
#     next_cursor = (
#         query_iterator.next_page_token.decode('utf-8')
#         if query_iterator.next_page_token else None)

#     return entities, next_cursor

def _tratar_formatos(entidade: dict):
    """Converte os atributos de uma entidade nos tipos de dados esperados pela aplicação.

    Argumentos:
        entidade: dictionary que contém os atributos de uma entidade cujos atributos terão 
        os tipos de dados convertidos.
    Retorno:
        entidade com os tipos de dados convertidos.
    """
    # Varre o dicionário de nomes e formatos
    for atributo in entidade.items():
        # Tratamento de campos data
        if atributo.startswith('dt_'):
            # Converte o campo data para datetime
            entidade[atributo] = datetime.fromisoformat(entidade[atributo])
        if atributo.startswith('val_'):
            entidade[atributo] = Decimal(entidade[atributo])

    return entidade
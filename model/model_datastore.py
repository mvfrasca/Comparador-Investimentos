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

builtin_list = list


def init_app(app):
    pass

def get_client():
    # return datastore.Client(current_app.config['PROJECT_ID'])
    return datastore.Client()

def list_indicadores(dt_referencia=None):
    # Instancia o cliente do banco de dados NOSQL GCloud DataStore
    ds = get_client()
    # Prepara a query para consultar valores do índice IPCA
    query = ds.query(kind='Indicadores')
    # Inclui filtros da consulta caso passados
    if dt_referencia is not None:
        query.add_filter('dt_ult_referencia','<', dt_referencia)
    #Define ordenação da consulta
    query.order = ['dt_ult_referencia']
    # Executa a consulta e armazena num dictionary 
    #lista = list(query.fetch())
    lista = query.fetch()

    entities = builtin_list(map(from_datastore, lista))
    
    return entities

def list_indices(indicador, dataInicial, dataFinal):
    # Instancia o cliente do banco de dados NOSQL GCloud DataStore
    ds = get_client()
    # Prepara a query para consultar valores do índice IPCA
    query = ds.query(kind='Indices')
    # Inclui filtros da consulta
    query.add_filter('tp_indice','=',indicador)
    query.add_filter('dt_referencia','>=', dataInicial)
    query.add_filter('dt_referencia','<=', dataFinal)
    #Define ordenação da consulta
    query.order = ['dt_referencia']
    # Executa a consulta e armazena num dictionary 
    indices = list(query.fetch())

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

# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.name
    return entity
# [END from_datastore]


# [START list]
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
# # [END list]


def read(id):
    ds = get_client()
    key = ds.key('Indice', id)
    results = ds.get(key)
    return from_datastore(results)

def read_indicador(id):
    ds = get_client()
    key = ds.key('Indicadores', id)
    results = ds.get(key)
    return from_datastore(results)
    #return results

# [START update]
def update(kind, data, id=None):
    ds = get_client()
    if id:
        key = ds.key(kind, id)
    else:
        key = ds.key(kind)

    # entity = datastore.Entity(
    #     key=key) ,
    #     exclude_from_indexes=['description'])
        
    entity = datastore.Entity(key=key)

    entity.update(data)
    ds.put(entity)
    
    #return from_datastore(entity)
    return key


create = update
# [END update]


def delete(id):
    ds = get_client()
    key = ds.key('Indices', int(id))
    ds.delete(key)


# [START update]
def update_multi(kind, lista):
    ds = get_client()

    entities = []
    for item in lista:
        key = ds.key(kind, item['id'])
        entity = datastore.Entity(key=key)
        entity.update(item)
        entities.append(entity)
    
    ds.put_multi(entities)
    
    #return from_datastore(entity)
    return
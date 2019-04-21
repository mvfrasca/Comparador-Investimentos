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

    @classmethod
    def values(cls):
        lista = []
        for item in cls.__members__.values():
	        lista.append(item.value)
        lista.sort()
        return lista

def init_app(app):
    pass

def get_client():
    # return datastore.Client(current_app.config['PROJECT_ID'])
    return datastore.Client()

def list_indexadores(dt_referencia :datetime.date=None, tipo_atualizacao: str=None):
    # Instancia o cliente do banco de dados NOSQL GCloud DataStore
    ds = get_client()
    # Prepara a query para consultar valores do índice IPCA
    query = ds.query(kind=TipoEntidade.INDEXADORES.value)
    # Inclui filtros da consulta caso passados
    if dt_referencia is not None:
        query.add_filter('dt_ult_referencia','<', dt_referencia.isoformat())
    if tipo_atualizacao is not None:
        query.add_filter('tipo_atualizacao','=', tipo_atualizacao)
    #Define ordenação da consulta
    query.order = ['dt_ult_referencia']
    # Executa a consulta e armazena num dictionary 
    #lista = list(query.fetch())
    lista = query.fetch()

    entities = builtin_list(map(from_datastore, lista))
    
    return entities

def list_indices(indexador :str, dataInicial :datetime.date, dataFinal : datetime.date):
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
    # indices = list(query.fetch())
    indices = query.fetch()
    # Trata os formatos retornados da lista de entidades
    # indices = list(map(lambda e: _tratar_formatos(e), indices))
    indices = builtin_list(map(from_datastore, indices))
    return indices

def read(kind: TipoEntidade, id: str):
    ds = get_client()
    key = ds.key(kind.value, id)
    results = ds.get(key)
    return from_datastore(results)

def update(kind: TipoEntidade, data: dict, id: str = None):
    ds = get_client()
    entidade = to_datastore(ds, kind, data)
    ds.put(entidade)
    return

create = update

def delete(kind: TipoEntidade, id: str):
    ds = get_client()
    key = ds.key(kind.value, id)
    ds.delete(key)
    return key

def update_multi(kind: TipoEntidade, lista: list):
    ds = get_client()
    entidades = []
    for item in lista:
        entidade = to_datastore(ds, kind, item)
        entidades.append(entidade)
    ds.put_multi(entidades)
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

#######################################################################################################
# Funções auxiliares para tratamento dos dados retornados do banco de dados ou a serem consistidos 
# no banco de dados
#######################################################################################################

# Tratamento de dados recebidos do banco de dados para os padrões da api
def from_datastore(entity):
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
    entity = _tratar_formatos(entity.copy())

    return entity

# Tratamento de dados recebidos do banco de dados para os padrões da api
def _tratar_formatos(entidade: dict):
    """Converte os atributos de uma entidade nos tipos de dados esperados pela API.

    Argumentos:
        entidade: dictionary que contém os atributos de uma entidade cujos atributos terão 
        os tipos de dados convertidos.
    Retorno:
        entidade com os tipos de dados convertidos.
    """
    # Define a precisão da classe Decimal para 9 casas decimais
    getcontext().prec = 9
    # Varre os atributos da entidade
    for atributo in entidade.keys():
        # Tratamento de campos data e data
        if atributo.startswith('dt_'):
            entidade[atributo] = datetime.fromisoformat(entidade[atributo]).date()
        # Tratamento de campos data e data/hora
        elif atributo.startswith('dth_'):
            entidade[atributo] = datetime.fromisoformat(entidade[atributo])
        elif atributo.startswith('val_'):
            entidade[atributo] = Decimal(entidade[atributo])
    return entidade

# Tratamento de dados a serem consistidos no banco de dados
def to_datastore(ds: datastore.Client, kind: TipoEntidade, entidade: dict):
    """Converte os dados a serem gravados do Google Datastore para o formato padronizado de cada tipo de campo.

    Retorno:
        Entidade do Google Datastore.
    """
    if not entidade:
        return None
    elif type(entidade) != dict:
        entidade = entidade.__dict__

    # Varre os atributos da entidade atualizando os padrões de tipos de dados
    for atributo in entidade.keys():
        if atributo == 'id':
            key = ds.key(kind.value, entidade['id'])
        # Tratamento de campos data e data/hora
        # elif atributo.startswith(('dt_','dth_')):
        #     # Converte o campo datatime para string no padrão ISO
        #     entidade[atributo] = entidade[atributo].isoformat()
        elif type(entidade[atributo]).__name__ == 'date':
            entidade[atributo] = entidade[atributo].isoformat()
        elif type(entidade[atributo]) == datetime:      
            entidade[atributo] = entidade[atributo].isoformat()

    # Se entidade não possuia campo 'id' gera chave automática do datastore
    if not key:
        key = ds.key(kind.value)
    # entity = datastore.Entity(
    #     key=key) ,
    #     exclude_from_indexes=['description'])
    # Cria uma entidade com a chave obtida
    entity = datastore.Entity(key=key)
    # Atualiza a entidade com os atributos recebidos no dictionary
    entity.update(entidade)

    return entity
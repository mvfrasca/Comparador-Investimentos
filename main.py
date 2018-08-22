# Copyright 2018 Google LLC
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

# [START gae_python37_app]
from flask import Flask, jsonify, request
from decimal import *
import os
import sqlite3


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

ipca = {     
        '2016-01': 1.27,
        '2016-02': 0.9,
        '2016-03': 0.43,
        '2016-04': 0.61,
        '2016-05': 0.78,
        '2016-06': 0.35,
        '2016-07': 0.52,
        '2016-08': 0.44,
        '2016-09': 0.08,
        '2016-10': 0.26,
        '2016-11': 0.18,
        '2016-12': 0.3,
        '2017-01': 0.38,
        '2017-02': 0.33,
        '2017-03': 0.25,
        '2017-04': 0.14,
        '2017-05': 0.31,
        '2017-06': -0.23,
        '2017-07': 0.24,
        '2017-08': 0.19,
        '2017-09': 0.16,
        '2017-10': 0.42,
        '2017-11': 0.28,
        '2017-12': 0.44,
        '2018-01': 0.29,
        '2018-02': 0.32,
        '2018-03': 0.09,
        '2018-04': 0.22
    }

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Comparador de Investimentos'

@app.route('/api/v1/resources/calc_invest', methods=['GET'])
def calcular_investimento():
    # Obtém argumentos
    query_parameters = request.args
    # Resgata o valor do investimento
    val_investimento = query_parameters.get('val_investimento')
    
    print(query_parameters.get('val_investimento'))

    # Valida se parâmetro do valor do investimento foi informado
    if not (val_investimento):
        return page_not_found(404)
    # Valida se parâmetro do valor do investimento é numérico  
    # if not str.isdecimal(val_investimento):
    #     return "Valor do investimento inválido. Informe um valor (utilize . para separação de decimais)" 
    
    # Define a precisão para 7 casas decimais
    getcontext().prec = 7

    # Testando a conversão para decimal já que o isnumeric e isdecimal não funcionou corretamente
    try:
        val_investimento = Decimal(val_investimento)
    except InvalidOperation:
        return "Valor do investimento inválido. Informe um valor numérico (utilize . (ponto) para separação de decimais)" 

    # Define a variável do dicionário que armazenará a evolução do valor investido mês a mês
    resultado_investimento = {}
    evolucao = {}
    i = 0
    # Varre o dicionário de índices para aplicar os índices mês a mês 
    for ano_mes, val_indice in ipca.items():
        val_indice = Decimal(val_indice) / Decimal(100)
        val_investimento = val_investimento + (val_investimento * val_indice)
        evolucao[i] = {'Ano/mês': str(ano_mes), 'Indice': str(val_indice), 'Valor': str(val_investimento)}
        i = i + 1
        print("Mês/Ano: {0}  |  Indice: {1:03.7}  |  Valor: {2:03.2f}".format(ano_mes, val_indice, val_investimento))
        
    resultado_investimento.update({'evolucao': evolucao})

    return jsonify(resultado_investimento=resultado_investimento)

# @app.route('/api/v1/resources/percursos/all', methods=['GET'])
# def api_all():
#     conn = sqlite3.connect('twt.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     all_books = cur.execute('SELECT * FROM percursos;').fetchall()

#     return jsonify(all_books)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>O recurso não pode ser encontrado.</p>", 404

# @app.route('/api/v1/resources/percursos', methods=['GET'])
# def api_filter():
#     query_parameters = request.args

#     id = query_parameters.get('id')
#     nome = query_parameters.get('published')
#     descricao = query_parameters.get('author')

#     query = "SELECT * FROM percursos WHERE"
#     to_filter = []

#     if id:
#         query += ' id=? AND'
#         to_filter.append(id)
#     if nome:
#         query += ' nome=? AND'
#         to_filter.append(nome)
#     if descricao:
#         query += ' descricao=? AND'
#         to_filter.append(descricao)
#     if not (id or nome or descricao):
#         return page_not_found(404)

#     query = query[:-4] + ';'

#     conn = sqlite3.connect('twt.db')
#     conn.row_factory = dict_factory
#     cur = conn.cursor()

#     results = cur.execute(query, to_filter).fetchall()

#     return jsonify(results)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

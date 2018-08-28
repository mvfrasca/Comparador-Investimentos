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

from model import get_model
from flask import Blueprint, redirect, render_template, request, url_for, jsonify
# Importanto classe para tratamento de números decimais
from decimal import *

# Criando blueprint do módulo da API
api = Blueprint('api', __name__)

# [START list]
# @api.route("/")
# def list():
#     token = request.args.get('page_token', None)
#     if token:
#         token = token.encode('utf-8')

#     books, next_page_token = get_model().list(cursor=token)

#     return render_template(
#         "list.html",
#         books=books,
#         next_page_token=next_page_token)
# # [END list]


# @api.route('/<id>')
# def view(id):
#     book = get_model().read(id)
#     return render_template("view.html", book=book)


# # [START add]
# @api.route('/add', methods=['GET', 'POST'])
# def add():
#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)

#         book = get_model().create(data)

#         return redirect(url_for('.view', id=book['id']))

#     return render_template("form.html", action="Add", book={})
# # [END add]


# @api.route('/<id>/edit', methods=['GET', 'POST'])
# def edit(id):
#     book = get_model().read(id)

#     if request.method == 'POST':
#         data = request.form.to_dict(flat=True)

#         book = get_model().update(data, id)

#         return redirect(url_for('.view', id=book['id']))

#     return render_template("form.html", action="Edit", book=book)


# @api.route('/<id>/delete')
# def delete(id):
#     get_model().delete(id)
#     return redirect(url_for('.list'))

@api.route('/investimento', methods=['GET'])
def calcular_investimento():
    # Obtém argumentos
    query_parameters = request.args
    # Resgata o valor do investimento
    val_investimento_inicial = query_parameters.get('val_investimento')

    #print(query_parameters.get('val_investimento'))

    # Valida se parâmetro do valor do investimento foi informado
    if not (val_investimento_inicial):
        return page_not_found(404)
    # Valida se parâmetro do valor do investimento é numérico  
    # if not str.isdecimal(val_investimento):
    #     return "Valor do investimento inválido. Informe um valor (utilize . para separação de decimais)" 
    
    # Define a precisão para 7 casas decimais
    getcontext().prec = 7

    # Testando a conversão para decimal já que o isnumeric e isdecimal não funcionou corretamente
    try:
        val_investimento_inicial = Decimal(val_investimento_inicial)
    except InvalidOperation:
        return "Valor do investimento inválido. Informe um valor numérico (utilize . (ponto) para separação de decimais)" 

    # Inicializa o valor de investimento atualizado onde serão aplicados índices por período
    val_investimento_atualizado = val_investimento_inicial

    # Executa a consulta e armazena num dictionary 
    indices = get_model().get_indices()
    #print(indices)
    
    # Define a variável do dicionário que armazenará a evolução do valor investido mês a mês
    resultado_investimento = {}
    evolucao = []
    i = 0
    # Varre o dicionário de índices para aplicar os índices mês a mês 
    for indice in indices:
        ano_mes = indice['ano_mes']
        val_indice = indice['val_indice']
        val_indice = Decimal(val_indice) / Decimal(100)
        val_investimento_atualizado = val_investimento_atualizado + (val_investimento_atualizado * val_indice)
        evolucao.append({'ano_mes': str(ano_mes), 'indice': str(val_indice), 'valor': str(val_investimento_atualizado)})
        i = i + 1
        #print("Mês/Ano: {0}  |  Indice: {1:03.7}  |  Valor: {2:03.2f}".format(ano_mes, val_indice, val_investimento_atualizado))

    rendimento_bruto = val_investimento_atualizado - val_investimento_inicial
    resultado_investimento.update({'val_investimento_inicial': str(val_investimento_inicial)})
    resultado_investimento.update({'val_investimento_atualizado': str(val_investimento_atualizado)})
    resultado_investimento.update({'rendimento_bruto': str(rendimento_bruto)})
    resultado_investimento.update({'evolucao': evolucao})    

    return jsonify(resultado_investimento)

# @api.route('/indice', methods=['GET'])
# def popular_indice():
#     # Instancia o cliente do banco de dados NOSQL GCloud DataStore
#     datastore_client = datastore.Client()
#     # Varre o dicionário de índices para aplicar os índices mês a mês 
#     for ano_mes, val_indice in ipca.items():
#         # Obtém uma chave para inclusão do novo índice
#         chave_indice = datastore_client.key('IPCA')
#         # Prepara a nova entidade instanciando-a 
#         indice = datastore.Entity(key=chave_indice)
#         # Define o valor da(s) propriedade(s) da entidade
#         indice['ano_mes'] = ano_mes
#         indice['val_indice'] = val_indice
#         # Insere o novo índice
#         datastore_client.put(indice)
        
#         # Padrão de consulta da API
#         # http://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json&dataInicial={dataInicial}&dataFinal={dataFinal}

#         # CDI (Diário)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial=01/08/2018&dataFinal=26/08/2018

#         # SELIC (Diário)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial=01/08/2018&dataFinal=26/08/2018

#         # IPCA (Mensal)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018

#         # IGPM (Mensal)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018
        
#         # INCC (Mensal)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.192/dados?formato=json&dataInicial=01/08/2016&dataFinal=26/08/2018
        
#         # Poupança (Mensal)
#         # https://api.bcb.gov.br/dados/serie/bcdata.sgs.196/dados?formato=json&dataInicial=01/01/2018&dataFinal=26/08/2018

#     return "Indice populado com sucesso!"
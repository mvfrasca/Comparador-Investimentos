import json
import os
from flask import jsonify
# Importa módulo para tratamento de data/hora
from datetime import datetime

# Get variavel de ambiente
def _variable(name):
    """Recupera variável de ambiente.

    Argumentos:
        name: Nome da variável de ambiente.
    Retorno:
        Valor da variável de ambiente.
    """
    try:
        name = os.environ[name]
        return name
    except KeyError:
        message  = _error("Variable does not exist.", 500)
        raise Exception(message)

    return os.environ[name]

# Tratamento da mensagem de retorno com error
def _error(body, statusCode):
    """Formata a mensagem de retorno HTTP de erro para formato padrão.

    Argumentos:
        message: mensagem de erro
        code: código HTTP DE retorno
    Retorno:
        Json com mensagem de retorno formatada.
    """
    response = {
        'statusCode': statusCode,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    return jsonify(response)

# Tratamento da mensagem de retorno com sucesso
def _success(body, statusCode):
    """Formata a mensagem de retorno HTTP de sucesso para formato padrão.

    Argumentos:
        message: mensagem de sucesso
        code: código HTTP DE retorno
    Retorno:
        Json com mensagem de retorno formatada.
    """
    response =  {
        'statusCode': statusCode,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    return jsonify(response)

# Limpar atributos vazios
def _clean_attributes(data):
    """Limpa atributos vazios.

    Argumentos:
        data: objeto que contém uma lista de valores.
    Retorno:
        Objeto data sem os atributos vazios. 
    """
    data_clean = dict((k, v) for k, v in data.items() if v)
    return data_clean
 
def _is_number(obj):
    """Valida se o objeto contém um número inteiro ou decimal.

    Argumentos:
        obj: objeto a ser validado.
    Retorno:
        True: se conter um número inteiro ou decimal.
        False: se não conter um número.
    """
    try:
        float(obj)
        return True
    except:
        pass
    return False

# Valida se string contém um número inteiro ou decimal
# "%d/%m/%Y"
def _is_date(obj, mascara: str):
    """Valida se o objeto informado é uma data ou data/hora válida.

    Argumentos:
        obj: objeto a ser validado. Ex.: '01/01/2018'
        mascara: máscara de data/hora do objeto. Ex.: '%d/%m/%Y'
    Retorno:
        True: se for uma data ou data/hora válida.
        False: se for inválida.
    """
    try:
        datetime.strptime(obj, mascara)
        return True
    except:
        pass
    return False

def _converter_datas_dict(item: dict, nomes_e_formatos: dict):
    """Converte os campos de data de um dictionary em datetime.

    Argumentos:
        item: item de um dictionary que contem campos data em formato string a serem convertidos 
        para datetime
        nomes_e_formatos: dictionary contendo os nomes dos nomes dos atributos de data e respectivos formatos a 
        serem convertidos para datetime. Ex.:
        {'dt_ult_referencia':'%d/%m/%Y', 'dt_ult_atualiz':'%d/%m/%Y'}
    Retorno:
        item com as datas convertidas.
    """
    # Varre o dicionário de nomes e formatos
    for atributo, formato in nomes_e_formatos.items():
        # Converte o campo data para datetime
        item[atributo] = datetime.strptime(item[atributo], formato)

    return item

class InputException(Exception):
    """Exceção disparada nos casos argumentos de entrada inválidos.

    Argumentos:
        expression: atributo inválido em que ocorreu o erro
        message: mensagem detalhando o motivo do erro
    """
    def __init__(self, atributo, mensagem):
        self.atributo = atributo
        self.mensagem = mensagem
    
    pass
    
class BusinessException(Exception):
    """Exceção disparada nos casos em que ocorre erros de validação de regras de negócio.

    Argumentos:
        codigo: código do erro de validação de regra de negócio
        mensagem: mensagem detalhando o motivo do erro
    """
    def __init__(self, codigo:str, mensagem:str):
        self.codigo = codigo
        self.mensagem = mensagem

    pass

class ServerException(Exception):
    """Exceção disparada nos casos em que ocorre erros internos na API e tratados de forma amigável ao lado cliente.
    
    Argumentos:
        mensagem: mensagem detalhando o motivo do erro. Quando não informada define mensagem padrão.
    """
    def __init__(self, exception: Exception = None, mensagem:str = None):
        if mensagem is None:
            self.mensagem = "Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde."
        else:
            self.mensagem = mensagem
    pass
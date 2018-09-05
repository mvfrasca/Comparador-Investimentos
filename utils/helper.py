import json
import os
from flask import jsonify
# Importa módulo para tratamento de data/hora
from datetime import datetime

# Get variavel de ambiente
def _variable(name):
    try:
        name = os.environ[name]
        return name
    except KeyError:
        message  = _error("Variable does not exist.", 500)

        raise Exception(message)


    return os.environ[name]

# Tratamento da mensagem de retorno com error
def _error(message, code):

    response =  {
        'statusCode': code,
        'body': { 'Message': message },
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    return jsonify(response)

# Tratamento da mensagem de retorno com sucesso
def _success(message, code):
    response =  {
        'statusCode': code,
        'body': message,
        'headers': {
            'Content-Type': 'application/json',
        },
    }
    return jsonify(response)

# Limpar atributos vazios
def _clean_attributes(data):
   data_clean = dict((k, v) for k, v in data.items() if v)
   return data_clean

# convert date to json
def _date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

# Valida se string contém um número inteiro ou decimal
def _is_number(obj):
    try:
        float(obj)
        return True
    except:
        pass
    return False

# Valida se string contém um número inteiro ou decimal
# "%d/%m/%Y"
def _is_date(obj, mascara):
    try:
        datetime.strptime(obj, mascara)
        return True
    except:
        pass
    return False

# Classe para tipificar exceções causadas pelo cliente
class ClientException(Exception):
    pass
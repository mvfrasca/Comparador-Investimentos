import json
import os
from flask import jsonify
# Importa módulo para tratamento de data/hora
from datetime import datetime, timezone
# Importanto módulo para tratamento de números decimais
from decimal import Decimal

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
        'body': _tratar_formatos(body),
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
        'body': _tratar_formatos(body),
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
# "%Y-%m-%d"
def _is_date(obj, mascara: str):
    """Valida se o objeto informado é uma data ou data/hora válida.

    Argumentos:
        obj: objeto a ser validado. Ex.: '01/01/2018'
        mascara: máscara de data/hora do objeto. Ex.: '%Y-%m-%d'
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
        item: item de um dictionary que contém campos data em formato string a serem convertidos 
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

# Converte uma string formatada de data em formato inteiro
def _strdate_to_int(data: str, mascara_entrada: str):
    """Converte uma string formatada em objeto datetime considerando o fuso horário pré-definido YYYYMMDD

    Argumentos:
        data: objeto a ser validado. Ex.: '01/01/2018'
        mascara_entrada: máscara de data/hora da string de entrada. Ex.: '%Y-%m-%d'
    Retorno:
        Inteiro represetando a Data no formato YYYYMMDD
    """
    try:
        # Converte o campo data para datetime
        date = datetime.strptime(data, mascara_entrada)
        # Converte a data para o formato inteiro esperado YYYYMMDD
        intdate = int(datetime.strftime(date, "%Y%m%d"))
        return intdate
    except:
        pass

# Converte um inteiro formatada de data em formato inteiro
def _strdate_to_int(data: str, mascara_entrada: str):
    """Converte uma string formatada em inteiro considerando formato pré-definido YYYYMMDD

    Argumentos:
        data: string de uma data formatada. Ex.: '01/01/2018'
        mascara_entrada: máscara de data/hora da string de entrada. Ex.: '%Y-%m-%d'
    Retorno:
        Inteiro representando a Data no formato YYYYMMDD
    """
    try:
        # Converte o campo data para datetime
        date = datetime.strptime(data, mascara_entrada)
        # Converte a data para o formato inteiro esperado YYYYMMDD
        intdate = int(datetime.strftime(date, "%Y%m%d"))
        return intdate
    except:
        pass

# Converte um inteiro formatada de data em formato inteiro
def _date_to_int(data: datetime):
    """Converte uma data em inteiro considerando formato pré-definido YYYYMMDD

    Argumentos:
        data: data no formato datetime
    Retorno:
        Inteiro representando a Data no formato YYYYMMDD
    """
    try:
        # Converte a data para o formato inteiro esperado YYYYMMDD
        intdate = int(datetime.strftime(data, "%Y%m%d"))
        return intdate
    except:
        pass

# Converte um inteiro formatada de data em formato inteiro
def _intdate_to_str(data: int, mascara_saida: str):
    """Converte inteiro que representa uma data em uma string com mascara solicitada

    Argumentos:
        data: string de uma data formatada. Ex.: '01/01/2018'
        mascara_saida: máscara de data/hora da string de saída. Ex.: '%Y-%m-%d'
    Retorno:
        String representando a data no formato solicitado
    """
    try:
        # Converte o campo data para datetime
        date = datetime.strptime(str(data), "%Y%m%d")
        # Converte a data para o formato de saída solicitado
        strdate = datetime.strftime(date, mascara_saida)
        return strdate
    except:
        pass

# Converte um inteiro formatada de data em formato inteiro
def _intdate_to_datetime(data: int):
    """Converte inteiro que representa uma data no formato YYYYMMDD em formato datetime

    Argumentos:
        data: inteiro que representa uma data no formato YYYYMMDD. Ex.: 20181231'
    Retorno:
        Data no formato datetime
    """
    try:
        # Converte o campo data para datetime
        date = datetime.strptime(str(data), "%Y%m%d")
        return date
    except:
        pass

# Tratamento de dados recebidos do banco de dados para os padrões da api
def _tratar_formatos(dado):
    """Converte os atributos de um retorno da API nos tipos de dados padrões de resposta da API.

    Argumentos:
        dados: lista ou dictionary que contém os dados de retorno cujos atributos terão 
        os tipos de dados convertidos.
    Retorno:
        Dados de retorno com tipos de dados dos atributos convertidos.
    """
    dado_convertido = None
    if type(dado) in (str, int):
        dado_convertido = dado
    elif type(dado) == datetime:      
        dado_convertido = dado.isoformat()
    elif type(dado) == Decimal:
        dado_convertido = float(dado)
    elif type(dado) == tuple:
	    dado_convertido = (dado[0], _tratar_formatos(dado[1]))
    elif type(dado) == list:
        dado_convertido = list(map(_tratar_formatos, dado))
    elif type(dado) == dict:
        dado_convertido = dict(map(_tratar_formatos, dado.items()))
    else:
        dado_convertido = dado
    
    return dado_convertido

# Tratamento de dados recebidos do banco de dados para os padrões da api
def _tratar_formato(atributo):
    """Converte o tipo de dado do atributo para o tipo de dados padrão de resposta da API.

    Argumentos:
        atributo: atributo cujo tipo de dado será convertido.
    Retorno:
        atributo com o tipo de dado convertido.
    """
    if type(atributo) == datetime:
        atributo = atributo.isoformat()
    elif type(atributo) == Decimal:
        atributo = float(atributo)
    
    return atributo
            

    # Varre os atributos da entidade
    for atributo in entidade.items():
        # Tratamento de campos data
        if atributo.startswith('dt_'):
            # Converte o campo data para datetime
            entidade[atributo] = datetime.fromisoformat(entidade[atributo])
        if atributo.startswith('val_'):
            entidade[atributo] = Decimal(entidade[atributo])

    return entidade

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
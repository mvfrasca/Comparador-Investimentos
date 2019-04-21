import json
from collections import OrderedDict

def jsonDefault(OrderedDict):
    return OrderedDict.__dict__

class BaseObject(object):
    """Classe base com alguns métodos padrão para dar suporte as integrações com o banco de dados.
    """
    def __init__(self,*args,**kwargs):
       pass
    
    # Datastore chama essa função pra buscar o conteúdo do argumento
    def __getitem__(self, key):
        return self.__dict__[key]

    # Datastore utiliza essa função para retornar a lista de chaves (keys) que se referem 
    # a cada atributo da classe
    def keys(self):
        return self.__dict__.keys()

    # Método para facilitar a serialização da classe em formato JSON
    @classmethod
    def fromDict(cls, dados:dict):
        if not isinstance(dados, dict):
            raise TypeError('fromDict: argumento deve ser dict')
        try:
            self = object.__new__(cls)
            # self._hashcode = -1
            for key in dados.keys():
                self.__dict__[key] = dados[key]
            return self
        except Exception:
            raise ValueError('Formato inválido de dados de entrada: {}'.format(dados))
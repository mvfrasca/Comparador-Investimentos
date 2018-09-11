class BaseObject(object):
    """Classe base com alguns métodos padrão para dar suporte as integrações com o banco de dados.
    """
    def __init__(self):
       self.__init__()
    
    # Datastore chama essa função pra buscar o conteúdo do argumento
    def __getitem__(self, key):
        return self.__dict__[key]

    # Datastore utiliza essa função para retornar a lista de chaves (keys) que se referem 
    # a cada atributo da classe
    def keys(self):
        return self.__dict__.keys()
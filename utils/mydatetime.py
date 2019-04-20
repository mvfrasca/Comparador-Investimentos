# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo de log
import logging

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe MyDateTime')
logger.setLevel(logging.INFO)

class mydatetime(datetime):
    """Classe que representa uma data/hora.
    
    Argumentos:
        tp_indice: tipo de índice (indexador). Ex.: ipca, poupanca, cdi.
        dt_referencia: data de referência do índice
        val_indice: valor do índice em percentual. Ex.: 0.0123
        dt_inclusao: data da inclusão do índice na base de dados de índices
    """
    # Método criador
    def from(self, dataHora: str, formato: str):
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.datahora = datetime.strptime(dataHora, formato)

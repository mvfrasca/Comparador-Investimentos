# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa a classe base
from baseobject import BaseObject

class Investimento(BaseObject):
    """Classe que representa um Investimento.
    
    Argumentos:
        valInvestimentoInicial: valor inicial do investimento
        indexador: nome identificador do indexador (ex.: ipca, selic)
        taxa: percentual aplicado sobre o índice (ex.: 130 (130% do cdi), 7 (IPCA + 7%))
        dataInicial: data inicial do investimento
        dataFinal (datetime): data de vencimento do investimento
    """
    # Método criador 
    def __init__(self, valInvestimentoInicial: Decimal, indexador: str, taxa: Decimal, dataInicial: datetime, dataFinal: datetime):
         # Define a precisão para 7 casas decimais
        getcontext().prec = 7
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.valInvestimentoInicial = Decimal(valInvestimentoInicial)
        self.indexador = indexador.lower()
        self.taxa = Decimal(taxa)
        self.dataInicial = dataInicial 
        self.dataFinal = dataFinal
        # Inicializa demais atributos da classe
        self.valSaldoBruto = Decimal(0)
        self.rentabilidadeBruta = Decimal(0)
        self.rentabilidadeBrutaAnual = Decimal(0)
        self.rentabilidadeLiquida = Decimal(0)
        self.rentabilidadeLiquidaAnual = Decimal(0)
        self.valImpostoRenda = Decimal(0)
        self.qtdDiasCorridos = int(0)
        self.valSaldoLiquido = Decimal(0)
        self.evolucao = []

    def calcular_investimento(self):
        """Realiza o cálculo do investimento em função do período informado.
    
        Retorno:
            Retorna uma lista contendo disctionaries referentes aos valores 
            de saldo e rentabilidade do investimento além de uma sublista 
            da evolução do valor inicial em função do tempo (período informado)
        """
        # Inicializa o valor de investimento atualizado onde serão aplicados índices por período
        self.valSaldoBruto = self.valInvestimentoInicial

        # Executa a consulta e armazena num dictionary 
        indices = get_model().list_indices(self.indexador, self.dataInicial, self.dataFinal)
        
        # Define a variável do dicionário que armazenará a evolução do valor investido de acordo 
        # com a peridicidade do índice (diariamente ou mensalmente)
        resultadoInvestimento = {}
        i = 0
        # Varre a lista de índices para aplicar os índices de acordo com a peridicidade do 
        # índice (diariamente ou mensalmente)
        for indice in indices:
            # Formata a data de referência
            data = datetime.strftime(indice['dt_referencia'], "%Y-%m-%d")
            # Formata o valor do índice
            valIndice = indice['val_indice']
            valIndice = Decimal(valIndice) / Decimal(100)
            # De acordo com o indexador carrega o valor do índice com a taxa informada
            if self.indexador == 'ipca':
                # Ex.: IPCA + 7%
                valIndice = valIndice + (valIndice * (self.taxa / Decimal(100)))
            elif self.indexador in ['cdi', 'selic']:
                # Ex.: 130% di CDI
                valIndice = valIndice * (self.taxa / Decimal(100))
            # Atualizado Saldo Bruto do investimento aplicado a 
            self.valSaldoBruto = self.valSaldoBruto + (self.valSaldoBruto * valIndice)
            self.evolucao.append({'data': data, 'indice': float(valIndice), 'valor': float(self.valSaldoBruto)})
            i = i + 1
            #print("Mês/Ano: {0}  |  Indice: {1:03.7}  |  Valor: {2:03.2f}".format(ano_mes, val_indice, val_investimento_atualizado))

        # Atualiza resultados do investimento
        self.rentabilidadeBruta = self.valSaldoBruto - self.valInvestimentoInicial

        # Monta o dictionary com o resultado do investimento para retorno do método
        resultadoInvestimento.update({'valInvestimentoInicial': float(self.valInvestimentoInicial)})
        resultadoInvestimento.update({'valSaldoBruto': float(self.valSaldoBruto)})
        resultadoInvestimento.update({'rentabilidadeBruta': float(self.rentabilidadeBruta)})
        resultadoInvestimento.update({'evolucao': self.evolucao})

        # for index, item in enumerate(times_ordenados, start=1):
        #     item['class_gols_pro_mand'] = index 

        return resultadoInvestimento


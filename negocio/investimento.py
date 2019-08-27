# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext, ROUND_HALF_UP
# Importa módulo para tratamento de data/hora
from datetime import datetime, timedelta
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa classe para Enumeradores
from enum import Enum
# Importa a classe base
from negocio.baseobject import BaseObject
from negocio.gestaocadastro import GestaoCadastro
from negocio.indexador import TipoIndexador
# Import o módulo para cálculos matemáticos
import math
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
from utils.helper import BusinessException

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
    def __init__(self, tipoInvestimento: str, valInvestimentoInicial: Decimal, indexador: str, taxa: Decimal, dataInicial: datetime, dataFinal: datetime):
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        # Atualiza os atributos com os valores informados na instanciação da classe
        self.tipoInvestimento = tipoInvestimento
        self.valInvestimentoInicial = Decimal(valInvestimentoInicial)
        self.indexador = indexador
        self.taxa = Decimal(taxa)
        self.dataInicial = dataInicial
        self.dataFinal = dataFinal
        # Inicializa demais atributos da classe
        self.valSaldoBruto = Decimal(0)
        self.rentabilidadeBruta = Decimal(0)
        self.rentabilidadeBrutaAnual = Decimal(0)
        self.rentabilidadeLiquida = Decimal(0)
        self.rentabilidadeLiquidaAnual = Decimal(0)
        self.percImpostoRenda = Decimal(0)
        self.valImpostoRenda = Decimal(0)
        self.percIOF = Decimal(0)
        self.valIOF = Decimal(0)
        self.qtdDiasCorridos = int(0)
        self.valSaldoLiquido = Decimal(0)
        self.evolucao = []

    def calcular_investimento(self):
        """Realiza o cálculo do investimento em função do período informado.
    
        Retorno:
            Retorna uma lista contendo dictionaries referentes aos valores 
            de saldo e rentabilidade do investimento além de uma sublista 
            da evolução do valor inicial em função do tempo (período informado)
        """
        # Validação - data inicial mínima
        if self.dataInicial < datetime(2001, 1, 1).date():
            mensagem  = "Data inicial do investimento deve ser maior ou igual a 01/01/2001."
            raise BusinessException('BE001', mensagem)
        # Validação - data final máxima
        elif self.dataFinal > datetime(2078, 12, 31).date():
            mensagem  = "Data final do investimento não pode ser maior que 31/12/2078."
            raise BusinessException('BE002', mensagem)
        # Validação - período de investimento
        elif self.dataFinal <= self.dataInicial:
            mensagem  = "Data final do investimento deve ser maior que a data inicial."
            raise BusinessException('BE003', mensagem)
        # Validação - Valor inicial de investimento
        elif self.valInvestimentoInicial <= Decimal(0):
            mensagem  = "Valor inicial do investimento deve ser maior que 0 (zero)."
            raise BusinessException('BE004', mensagem)
        # Validação - Tipo de investimento inválido
        elif self.tipoInvestimento.lower() not in TipoInvestimento.values():
            mensagem  = "Tipo de investimento inválido [{0}]. Tipos esperado: {1}.".format(self.tipoInvestimento.lower(), TipoInvestimento.values())
            raise BusinessException('BE005', mensagem)
        # Validação - Tipo de indexador inválido
        elif self.indexador.lower() not in TipoIndexador.values():
            mensagem  = "Tipo de indexador inválido [{0}]. Tipos esperado: {}.".format(self.indexador.lower(), TipoIndexador.values())
            raise BusinessException('BE006', mensagem)
        # Validação - Taxa inválida
        elif self.taxa <= Decimal(0) and self.indexador.lower() != 'poupanca':
            mensagem  = "Taxa do investimento não pode ser igual ou menor que 0 (zero)."
            raise BusinessException('BE007', mensagem)

        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        getcontext().rounding = ROUND_HALF_UP

        # Inicializa o valor de investimento atualizado onde serão aplicados índices por período
        self.valSaldoBruto = self.valInvestimentoInicial

        objCadastro = GestaoCadastro()
        # Executa a consulta e armazena num dictionary 
        indices = objCadastro.list_indices(self.indexador.lower(), self.dataInicial - timedelta(days=1), self.dataFinal)
        
        # Calcula a quantidade de dias corridos do investimento
        self.qtdDiasCorridos = (self.dataFinal - self.dataInicial).days

        # Define a variável do dicionário que armazenará a evolução do valor investido de acordo 
        # com a peridicidade do índice (diariamente ou mensalmente)
        resultadoInvestimento = {}
        i = 0
        # Varre a lista de índices para aplicar os índices de acordo com a peridicidade do 
        # índice (diariamente ou mensalmente)
        for indice in indices:
            # Formata a data de referência
            data = indice['dt_referencia']
            # Formata o valor do índice
            valIndice = indice['val_indice']
            valIndice = Decimal(valIndice)
            # De acordo com o indexador carrega o valor do índice com a taxa informada
            if self.indexador.lower() in ['ipca', 'igpm']:
                # Ex.: IPCA + 7%
                taxaMensal = self.taxaAnualToMensal(self.taxa)
                valIndice = valIndice + taxaMensal
            elif self.indexador.lower() in ['cdi', 'selic']:
                # Ex.: 130% do CDI
                valIndice = valIndice * (self.taxa / Decimal(100))
            # Atualizado Saldo Bruto do investimento
            self.valSaldoBruto = self.valSaldoBruto * (1 + (valIndice / Decimal(100)))
            self.valSaldoBruto = Decimal(round(float(self.valSaldoBruto),2))

            self.evolucao.append({'data': data, 'indice': float(valIndice), 'valor': float(self.valSaldoBruto)})
            i = i + 1
            #print("Mês/Ano: {0}  |  Indice: {1:03.7}  |  Valor: {2:03.2f}".format(ano_mes, val_indice, val_investimento_atualizado))
        
        ### Atualiza resultados do investimento ###
        # Rentabilidade bruta
        self.rentabilidadeBruta = self.valSaldoBruto - self.valInvestimentoInicial
        # Imposto de renda
        if self.tipoInvestimento.lower() in ['poupanca', 'lci', 'lca']:
            self.percImpostoRenda = Decimal(0)
        else:
            self.percImpostoRenda = self.obterPercIR(self.qtdDiasCorridos)
        self.valImpostoRenda = self.rentabilidadeBruta * (self.percImpostoRenda / Decimal(100))
        # IOF
        # TODO: Incluir obtenção do perc e cálculo de IOF de acordo com a qtdDiasCorridos
        # Rentabilidade Líquida
        self.rentabilidadeLiquida = self.rentabilidadeBruta - self.valImpostoRenda - self.valIOF
        # Saldo Líquido
        self.valSaldoLiquido = self.valInvestimentoInicial + self.rentabilidadeLiquida

        # Monta o dictionary com o resultado do investimento para retorno do método
        resultadoInvestimento.update({'tipoInvestimento': self.tipoInvestimento})
        resultadoInvestimento.update({'indexador': self.indexador})
        resultadoInvestimento.update({'taxa': float(self.taxa)})
        resultadoInvestimento.update({'valInvestimentoInicial': float(self.valInvestimentoInicial)})
        resultadoInvestimento.update({'dataInicial': self.dataInicial})
        resultadoInvestimento.update({'dataFinal': self.dataFinal})
        resultadoInvestimento.update({'valSaldoBruto': float(self.valSaldoBruto)})
        resultadoInvestimento.update({'rentabilidadeBruta': float(self.rentabilidadeBruta)})
        resultadoInvestimento.update({'percImpostoRenda': float(self.percImpostoRenda)})
        resultadoInvestimento.update({'valImpostoRenda': float(self.valImpostoRenda)})
        resultadoInvestimento.update({'percIOF': float(self.percIOF)})
        resultadoInvestimento.update({'valIOF': float(self.valIOF)})
        resultadoInvestimento.update({'valSaldoLiquido': float(self.valSaldoLiquido)})
        resultadoInvestimento.update({'rentabilidadeLiquida': float(self.rentabilidadeLiquida)})
        resultadoInvestimento.update({'evolucao': self.evolucao})

        # for index, item in enumerate(times_ordenados, start=1):
        #     item['class_gols_pro_mand'] = index 

        return resultadoInvestimento

    @classmethod
    def taxaAnualToMensal(cls, taxaAnual:Decimal):
        """Converte uma taxa anual em taxa mensal.

        Argumentos: 
            taxaAnual: taxa Anual a ser convertida
        Retorno:
            Retorna um decimal representando a taxa mensal calculada.
        """
        taxaAnual = taxaAnual / Decimal(100) 
        taxaMensal = Decimal(0)
        tempTaxaAnual = Decimal(1) + taxaAnual 
        taxaMensal = Decimal(math.pow(tempTaxaAnual, (Decimal(1 / 12))) - 1)
        taxaMensal = taxaMensal * Decimal(100)

        return taxaMensal
    
    @classmethod
    def taxaMensalToDiaria(cls, taxaMensal:Decimal, diasUteisMes:Decimal):
        """Converte uma taxa mensal em taxa diária.
    
        Argumentos: 
            taxaMensal: taxa Mensal a ser convertida
            diasUteisMes: quantidade de dias úteis no mês
        Retorno:
            Retorna um decimal representando a taxa diária calculada.
        """
        taxaMensal = taxaMensal / Decimal(100) 
        taxaDiaria = Decimal(0)
        tempTaxaMensal = Decimal(1) + taxaMensal 
        taxaDiaria = Decimal(math.pow(tempTaxaMensal, (Decimal(1 / diasUteisMes))) - 1)
        taxaDiaria = taxaDiaria * Decimal(100)

        return taxaDiaria

    def obterPercIR(self, qtdDiasCorridos:int):
        """Identifica o percentual de Imposto de renda aplicável de acordo com a quantidade 
        de dias corridos do investimento.
    
        Retorno:
            Retorna um decimal representando o percentual de IR a ser aplicado sob o rendimento
            do investimento.
        """
        # Define a precisão para 9 casas decimais
        getcontext().prec = 9
        percIR = Decimal(0)

        # TODO: criar entidade no banco de dados com os intervalos e respectivos % para flexibilizar 
        # manutenção dos intervalos e %s
        if qtdDiasCorridos <= 180:
            percIR = 22.5
        elif qtdDiasCorridos <= 360:
            percIR = 20
        elif qtdDiasCorridos <= 720:
            percIR = 17.5
        else:
            percIR = 15
        
        return Decimal(percIR)

# Enum de tipos de investimento - para evitar buscas excessivas no banco dado que não não mudam tanto
class TipoInvestimento(Enum):
    ''' Enum que define os tipos das investimentos disponíveis para cálculo
    '''
    POUPANCA = 'poupanca'
    CDB = 'cdb'
    LCI = 'lci'
    LCA = 'lca'

    @classmethod
    def values(cls):
        lista = []
        for item in cls.__members__.values():
	        lista.append(item.value)
        lista.sort()
        return lista

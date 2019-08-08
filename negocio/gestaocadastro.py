# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa módulo para operações com datas
from dateutil import relativedelta
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model
# Importa módulo para tratamento de arquivos json
import json
# Importa módulo para tratamento de arquivos csv
import csv
# Importa o módulo Helper
import utils.helper
from utils.helper import _converter_datas_dict
from utils.helper import BusinessException
from utils.helper import ServerException
# Importa o módulo de log
import logging
# Importa a classe base
from negocio.baseobject import BaseObject
# Importa outras classes de negócio
from negocio.bancocentral import BancoCentral
from negocio.indice import Indice
from negocio.indexador import Indexador, TipoIndexador, TipoAtualizacao
from negocio.calendario import Calendario
from negocio.feriado import Feriado

# Inicializa o objeto para gravação de logs
logger = logging.getLogger('Classe GestaoCadastro')
logger.setLevel(logging.INFO)

class GestaoCadastro(BaseObject):
    """Classe que gerencia os cadastros que dão suporte aos cálculos de investimento.
    """
    def __init__(self):
       pass
    
    def put_feriados(self):
        """Realiza a carga inicial das entidades que representarão os feriados bancários.
           CSV extraído de http://www.anbima.com.br/feriados/feriados.asp
        Retorno:
            Quantidade de feriados incluidos.
        """
        # Carrega arquivo CSV que contém a carga inicial dos feriados
        with open(r'''static\csv\feriados.csv''',encoding='ANSI') as f:
            reader = csv.reader(f, delimiter=';')
            feriados = []
            tipoEntidade = get_model().TipoEntidade.FERIADOS
            contador = 0
            for linha in reader:
                # Recupera atributo data da linha do arquivo e formata com padrão de datetime.date
                dt_feriado = datetime.strptime(linha[0], "%d/%m/%Y").date()
                # Prepara o dicionário com os atributos da entidade feriado
                feriado = {'id': int(datetime.strftime(dt_feriado,'%Y%m%d')), 'dt_feriado': dt_feriado, 'descricao': linha[2]}
                feriados.append(feriado)
                if len(feriados) == 100:
                    # Inclui/atualiza a base de dados com os indexadores        
                    get_model().update_multi(tipoEntidade, feriados)
                    # Atualiza contador de inserções
                    contador+= len(feriados)
                    # Loga os estado atual da carga
                    logger.info("Carga inicial de feriados. Qtd. parcial carregada: {}".format(contador))
                    # Limpa a lista de feriados para nova inclusão parcial
                    feriados.clear()            
            else:
                # Inclui/atualiza a base de dados com os indexadores        
                get_model().update_multi(tipoEntidade, feriados)
                # Atualiza contador de inserções
                contador+= len(feriados)
                # Loga os estado atual da carga
                logger.info("Carga inicial de feriados. Qtd. parcial carregada: {}".format(contador))
                # Limpa a lista de feriados para nova inclusão parcial
                feriados.clear()   

            # Loga os estado atual do indicador
            logger.info("Carga inicial de feriados. Qtd. feriados carregada: {}".format(contador))

        return contador

    def get_feriados(self, dataInicial: datetime.date, dataFinal: datetime.date):
        """Obtém a lista de feriados existentes entre as datas inicial e final informadas.
        
        Argumentos:
            - dataInicial: data inicial do período para consulta aos feriados
            - dataFinal: data final do período para consulta aos feriados
        Retorno:
            - lista de feriados referente ao período solicitado.
        """
        # Obtém a lista de feriados do período solicitado
        feriados = list(map(Feriado.fromDict, get_model().list_feriados(dataInicial, dataFinal)))

        return feriados

    def put_indexadores(self):
        """Realiza a carga inicial das entidades que representarão os indexadores.
    
        Retorno:
            Retorna uma lista contendo os indexadores que foram inclusos.
        """
        # Carrega arquivo JSON que contém a carga inicial dos indexadores
        with open(r'''static\json\indexadores.json''',encoding='UTF8') as f:
            indexadores = json.load(f)
            # indexadores = list(map(lambda x: dict(x.keys(), x.values()), list(f)))
            # Prepara o dicionário com os nomes dos campos data e respectivo formato no json
            # para que a função _converter_datas_dict realize a conversão para datetime
            datas_converter = {'dt_ult_referencia':'%d/%m/%Y', 'dth_ult_atualiz':'%d/%m/%Y'}
            indexadores = list(map(lambda item: _converter_datas_dict(item, datas_converter), indexadores))
            # Loga os estado atual do indicador
            logger.info("Carga inicial de indexadores")
            # Inclui/atualiza a base de dados com os indexadores
            tipoEntidade = get_model().TipoEntidade.INDEXADORES
            get_model().update_multi(tipoEntidade, indexadores)

        return
    
    def put_indexador(self, indexador: Indexador):
        """Inclui/atualiza os dados de um indexador.
        """
        if not isinstance(indexador, Indexador):
            raise TypeError('put_indexador: argumento deve ser do tipo Indexador')
        try: 
            tipoEntidade = get_model().TipoEntidade.INDEXADORES
            get_model().update(tipoEntidade, indexador, indexador.id)
        except Exception as e:
            raise ServerException(e)

    def get_indexadores(self, dataReferencia: datetime=None, tipoAtualizacao: TipoAtualizacao=None):
        """Obtém a lista de indexadores disponíveis cuja data de última atualização é anterior ao argumento dataReferencia.
        
        Argumentos:
            - dataReferencia: data de referencia que limita a consulta aos indexadores cuja data de última 
            atualização seja anterior ao referido argumento. Quando não informada ou for informada como None,
            todos os indexadores cadastrados são retornados.
            - tipoAtualizacao: tipo de atualização dos índices: automática (consulta à API do Banco Central) ou calculada a 
            partir de de outro índice com periodicidade diferente.
        """
        strTipoAtualizacao = None
        if tipoAtualizacao is not None:
            strTipoAtualizacao = tipoAtualizacao.value

        # Obtém a lista de indexadores para atualização (cuja data de última atualização é anterior à dt_referencia)
        indexadores = list(map(Indexador.fromDict, get_model().list_indexadores(dataReferencia, strTipoAtualizacao)))

        return indexadores

    def get_indexador(self, id: str):
        """Retorna o indexador de acordo com o id solicitado

        Argumentos:
            id: código identificador do indexador. Ex.: ipca, cdi, poupanca.
        """
        # Obtém os dados do indexador solicitado
        tipoEntidade = get_model().TipoEntidade.INDEXADORES
        indexador = Indexador.fromDict(get_model().read(tipoEntidade, id.lower()))
        print('')
        print('INDEXADOR: {0}, nome: {1}'.format(indexador, type(indexador)))
        return indexador
    
    def put_indice(self, indice: Indice):
        """Inclui/atualiza os dados de um índice.
        """
        if not isinstance(indice, Indice):
            raise TypeError('put_indice: argumento deve ser do tipo Indice')
        try: 
            tipoEntidade = get_model().TipoEntidade.INDEXADORES
            get_model().update(tipoEntidade, indice, indice.id)
        except Exception as e:
            raise ServerException(e)

    def put_indices(self, indexador: Indexador, indices: list):
        """Inclui/atualiza índices em lote.
        """
        if not isinstance(indexador, Indexador):
            raise TypeError('put_indices: argumento indexador deve ser do tipo Indexador')
        if not isinstance(indices, list):
            raise TypeError('put_indices: argumento indices deve ser do tipo list contendo objetos do tipo Indice')
        try:
            
            tipoEntidade = get_model().TipoEntidade.INDICES
            contador = 0
            while(len(indices) > 0):
                # Limita em 100 a quantidade de índices a consistir
                if len(indices) >= 100:
                    qtd = 100
                else:
                    qtd = len(indices)
                indicesConsistir = indices[0:qtd]
                # Inclui/atualiza índices em lote
                get_model().update_multi(tipoEntidade, indicesConsistir)
                # Atualiza contador de inserções
                contador+= qtd
                # Limpa índices consistidos
                for i in range(qtd):
                    ult_indice_removido = indices.pop(0)
                # Atualiza a data do último índice armazenado na entidade do indexador correspondente 
                # para controle de próximas atualizações
                indexador.dt_ult_referencia = ult_indice_removido.dt_referencia
                indexador.dth_ult_atualiz = datetime.now()
                indexador.qtd_regs_ult_atualiz = qtd
                self.put_indexador(indexador)
            
            return contador
            
        except Exception as e:
            raise ServerException(e)

    def list_indices(self, indexador: str, dataInicial: datetime.date, dataFinal: datetime.date):
        """Retorna o indexador de acordo com o id solicitado

        Argumentos:
            indexador: código identificador do indexador. Ex.: ipca, cdi, poupanca.
            dataInicial: data inicial do período de índices a ser consultado.
            dataFinal: data final do período de índices a ser consultado.
        """
        # Obtém os dados dos índices solicitados 
        # Executa a consulta e armazena num dictionary 
        indices = get_model().list_indices(indexador, dataInicial, dataFinal)

        return indices

    def atualizar_indices(self):
        """Atualiza os índices dos indexadores cadastrados. Obtém os índices atualizados desde a 
        última data de referência importada da API do Banco Central.
        """
        try:
            # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
            # zerados caso contrário datastore não reconhece)
            dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
            contador = 0
            # Obtém a lista de indexadores com tipo e atualizaçaõ AUTOMÁTICA 
            # cuja data de última atualização é anterior à data atual
            indexadores = self.get_indexadores(dataAtual, TipoAtualizacao.AUTOMATICA)

            # Percorre os indexadores para consulta e atualização
            for indexador in indexadores:
                # Loga os estado atual do indexador
                logger.info('Indexador a receber atualização de índices: {}'.format(indexador))
                # Caso o índicador seja de peridicidade mensal e o mês da última atualização é igual ao 
                # mês atual pula para o próximo indexador
                # if (periodicidade.lower() == 'mensal') and (datetime.strftime(dataAtual, "%Y%m") == datetime.strftime(dataUltReferencia, "%Y%m")):
                #     # Pula para o próximo indexador
                #     continue
                # Instancia a classe de negócios responsável pela consulta à API do Banco Central
                objBC = BancoCentral()
                # Recupera indices disponíveis do indexador desde a última atualização até hoje 
                indicesBC = objBC.list_indices(indexador.serie, indexador.dt_ult_referencia, dataAtual)
                # Inicializa coleção e contador de inserções/atualizações
                indices = []
                # Varre a lista de índices retornadas pela API
                for indiceBC in indicesBC:
                    logger.info('Índice a ser atualizado Banco Central: {0}, qtd: {1}, dados: {2}'.format(indexador.nome, len(indiceBC), indiceBC))
                    # Recupera as propriedades do índice (data e valor)
                    dataReferencia = indiceBC['data']
                    valorIndice = float(indiceBC['valor'])
                    # Verifica se data de referência do índice é anterior à data da última atualização 
                    # e caso positivo pula para o próximo (API do BC retornar sempre um dia pra tras)]
                    # if (dataReferencia.isocalendar() <= dataUltReferencia.isocalendar()):
                    #     logger.info('Índice descartado por ser anterior a última atualização')
                    #     continue      
                    # Popula uma instancia de índice a ser consistida
                    indice = Indice(tp_indice = indexador.id, dt_referencia = dataReferencia, val_indice = valorIndice, dth_inclusao = datetime.now())
                    # Inclui o índice na coleção de índices a ser consistida em banco de dados
                    indices.append(indice)
                
                # Inclui / Atualiza os índices em lote
                contador+= self.put_indices(indexador, indices)

            return contador

        except BusinessException as be:
            raise be
        except Exception as e:
            raise ServerException(e)
                
    def atualizar_indices_calculados(self):
        """Atualiza os índices dos indexadores cujo tipo de atualização é calculada para periodicidade Diária 
        a partir dos índices de periodicidade Mensal. 
        """
        try:
            # Define a data para referência da consulta (utiliza fromisoformat para buscar data com hora/minuto/segundo 
            # zerados caso contrário datastore não reconhece)
            dataAtual = datetime.fromisoformat(datetime.now().date().isoformat())
            contador = 0
            # Obtém a lista de indexadores com tipo e atualizaçaõ AUTOMÁTICA 
            # cuja data de última atualização é anterior à data atual
            indexadores = self.get_indexadores(dataAtual, TipoAtualizacao.CALCULADA)

            # Percorre os indexadores para consulta e atualização
            for indexador in indexadores:
                # Loga os estado atual do indexador
                logger.info('Indexador a receber atualização de índices CALCULADOS: {}'.format(indexador))

                # Recupera indices disponíveis do indexador referenciado que possui os índices Mensais 
                # desde a última atualização até hoje 
                indicesMensais = self.list_indices(indexador.id_indexador_referenciado, indexador.dt_ult_referencia, dataAtual)
                # Inicializa coleção e contador de inserções/atualizações
                indices = []
                # Varre a lista de índices retornadas pela API
                for indiceMensal in indicesMensais:
                    # Define data inicial de pesquisa de dias úteis
                    dataInicial = indiceMensal['dt_referencia']
                    # Define data final de pesquisa de dias úteis
                    dataFinal = dataInicial + relativedelta(day=31)
                    # Obtém a lista de dias úteis no mês
                    diasUteis = Calendario.listDiasUteis(dataInicial, dataFinal)
                    # Obtém a qtd de dias úteis no mês
                    qtdDiasUteis = float(len(diasUteis))

                    for dataReferencia in diasUteis:
                        # Obtém o valor do índice diário partindo do indice mensal com base na qtd de dias úteis
                        valorIndice = (1+float(indiceMensal['val_indice']))**(1/qtdDiasUteis)-1
                                            
                        logger.info('Índice Diário calculado: {0}, taxa Mensal: {1}, taxa Diária: {2}'.format(indexador.nome, indiceMensal['val_indice'], valorIndice))
                        # Popula uma instancia de índice a ser consistida
                        indice = Indice(tp_indice = indexador.id, dt_referencia = dataReferencia, val_indice = valorIndice, dth_inclusao = datetime.now())
                        # Inclui o índice na coleção de índices a ser consistida em banco de dados
                        indices.append(indice)
                
                # Inclui / Atualiza os índices em lote
                contador+= self.put_indices(indexador, indices)

            return contador

        except BusinessException as be:
            raise be
        except Exception as e:
            raise ServerException(e)     
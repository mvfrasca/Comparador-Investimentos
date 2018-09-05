# Importanto módulo para tratamento de números decimais
from decimal import Decimal, getcontext
# Importa módulo para tratamento de data/hora
from datetime import datetime
# Importa o módulo responsável por selecionar o banco de dados conforme configuração no pacote model
from model import get_model

class GestaoCadastro:
    def __init__(self):
        self.__init__
    
    def criarIndicadores(self):
        # if request.method == 'POST':
        #     data = request.form.to_dict(flat=True)

        #     book = get_model().create(data)

        #     return redirect(url_for('.view', id=book['id']))
        
        # with open('static\json\indicadores.json') as f:
        #     indicadores = f.buffer().json()
        #     # indicadores = list(map(lambda x: dict(x.keys(), x.values()), list(f)))
        # print(indicadores)
        # get_model().update_multi("Indicadores", indicadores)

        keys = []
        # Poupança
        indicador = {}
        indicador.update({'nome': 'Poupança'})
        indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indicador.update({'periodicidade': 'mensal'})
        indicador.update({'serie': '196'})
        indicador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indicadores', indicador, 'poupanca')
        keys.append({key})
        print(indicador)
        # IPCA
        indicador = {}
        indicador.update({'nome': 'IPCA'})
        indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indicador.update({'periodicidade': 'mensal'})
        indicador.update({'serie': '433'})
        indicador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indicadores', indicador, 'ipca')
        keys.append({key})
        # CDI
        indicador = {}
        indicador.update({'nome': 'CDI'})
        indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indicador.update({'periodicidade': 'diario'})
        indicador.update({'serie': '12'})
        indicador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indicadores', indicador, 'cdi')
        keys.append({key})
        # SELIC
        indicador = {}
        indicador.update({'nome': 'SELIC'})
        indicador.update({'dt_ult_referencia': datetime.strptime('01/01/1900', "%d/%m/%Y")})
        indicador.update({'periodicidade': 'diario'})
        indicador.update({'serie': '12'})
        indicador.update({'qtd_regs_ult_atualiz': 0})
        key = get_model().create('Indicadores', indicador, 'selic')
        keys.append({key})
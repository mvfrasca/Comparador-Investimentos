# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import traceback
from model import get_model
from flask import current_app, Flask, redirect, url_for
# Importa o módulo Helper
import utils.helper
from utils.helper import _error
from utils.helper import InputException
from utils.helper import BusinessException
from utils.helper import ServerException

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        # Inicializa o objeto para gravação de logs
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('Controller API')
        logger.setLevel(logging.INFO)

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)

    # Register the Bookshelf CRUD blueprint.
    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    # Define a rota padrão
    @app.route("/")
    def index():
        # return redirect(url_for('crud.list'))
        return 'Comparador de Investimentos'

    # Tratamento de erro para recurso não encontrado
    @app.errorhandler(404)
    def page_not_found(e):
        logger.error(traceback.format_exc(limit=5))
        mensagem = "O recurso requisitado não foi encontrado."
        resposta = {'ServerException': {'mensagem': mensagem}}
        return _error(resposta, 404), 404

    # Tratamento de erros para erro interno do servidor
    @app.errorhandler(500)
    def server_error(e):
        logger.error(traceback.format_exc(limit=5))
        mensagem = "Ocorreu um erro inesperado no servidor. Por favor tente novamente mais tarde."
        resposta = {'ServerException': {'mensagem': mensagem}}
        return _error(resposta, 500), 500
    
    # Tratamento de erros para erros internos tratados 
    @app.errorhandler(ServerException)
    def server_exception(e):
        logger.error(traceback.format_exc(limit=5))   
        resposta = {'ServerException': {'mensagem': e.mensagem}}
        return _error(resposta, 500), 500

    # Tratamento de erros gerados por dados de entrada incorretos ou incompletos  
    @app.errorhandler(InputException)
    def input_exception(e):
        logger.error(traceback.format_exc(limit=5))
        resposta = {'InputException': {'atributo': e.campo, 'mensagem': e.mensagem}}
        return _error(resposta, 400), 400

    # Tratamento de erros gerados por dados de entrada incorretos ou incompletos  
    @app.errorhandler(BusinessException)
    def business_exception(e):
        logger.error(traceback.format_exc(limit=5))
        resposta = {'BusinessException': {'codigo': e.atributo, 'mensagem': e.mensagem}}
        return _error(resposta, 400), 400

    return app
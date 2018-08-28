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

from flask import current_app, Flask, redirect, url_for

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

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
        return """
        <h1>404</h1><p>O recurso requisitado não foi encontrado: <pre>{}</pre>
        Veja o log completo de rastreamento.</p>
        """.format(e), 404

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        <h1>500</h1><p>Ocorreu um erro interno: <pre>{}</pre>
        Veja o log completo de rastreamento.</p>
        """.format(e), 500

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    # elif model_backend == 'cloudsql':
    #     from . import model_cloudsql
    #     model = model_cloudsql
    # elif model_backend == 'mongodb':
    #     from . import model_mongodb
    #     model = model_mongodb
    else:
        raise ValueError(
            "Banco de dados não configurado. "
            "Por favor especifique datastore")

    return model
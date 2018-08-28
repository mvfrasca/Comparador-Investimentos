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

from flask import current_app

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
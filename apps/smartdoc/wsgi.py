"""
WSGI config for apps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from smartdoc.const import CONFIG
from skywalking import agent, config

collector = CONFIG.get('SKYWALKING_COLLECTOR')
name = CONFIG.get('SKYWALKING_SERVICE_NAME')
group = CONFIG.get('SKYWALKING_GROUP')

if collector:
    init_params = {
        'agent_collector_backend_services': collector,
        'agent_name': name
    }
    if group:
        init_params['agent_name'] = f"{group}::{name}"
    config.init(**init_params)
    agent.start()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')

application = get_wsgi_application()


def post_handler():
    from common import event
    from common import job
    from common.models.db_model_manage import DBModelManage
    event.run()
    job.run()
    DBModelManage.init()


post_handler()






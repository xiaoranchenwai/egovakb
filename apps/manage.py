#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    from smartdoc.const import CONFIG
    from skywalking import agent, config

    try:
        collector = CONFIG.get('SKYWALKING_COLLECTOR')
        name = CONFIG.get('SKYWALKING_SERVICE_NAME')
        if collector:
            config.init(agent_collector_backend_services=collector, agent_name=name)
            agent.start()
    except Exception:
        pass

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartdoc.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()




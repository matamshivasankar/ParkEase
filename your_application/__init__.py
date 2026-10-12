"""Render default-start-command WSGI package.

Render's Python runtime resolves the default start command ``gunicorn
your_application.wsgi`` to the module ``your_application.wsgi`` exposing an
``application`` callable. This package provides that callable for ParkEase so
the service boots with no dashboard configuration.

Prefer an explicit Start Command instead:

    gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 100 run:app

If that is configured, this package can be deleted.
"""

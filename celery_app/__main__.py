"""Módulo Celery App do CrawJUD Automatização."""

from celery_app.main import main as main_entry

if __name__ == "__main__":
    main_entry()

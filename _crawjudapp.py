from tqdm import tqdm


def _main_app() -> None:
    from crawjud.celery_app import main

    main()


if __name__ == "__main__":
    try:
        _main_app()
    except KeyboardInterrupt:
        tqdm.write("Server stopped by user.")

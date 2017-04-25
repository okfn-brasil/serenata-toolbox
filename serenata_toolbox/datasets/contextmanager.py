from contextlib import contextmanager


@contextmanager
def status_message(message):
    print(message, end=' ')
    yield
    print('Done!')

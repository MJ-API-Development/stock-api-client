import functools


class Config:
    pass


@functools.lru_cache
def config_instance():
    return Config()

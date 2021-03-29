# -*- coding: UTF-8 -*-
from typing import Tuple

import redis
from larksuiteoapi import Store, Config, AppSettings, Logger, LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARN, LEVEL_ERROR, \
    DefaultLogger


class RedisStore(Store):

    def __init__(self):
        self.cli = redis.StrictRedis(host='localhost', port=6379, db=0)

    def get(self, key):  # type: (str) -> Tuple[bool, str]
        value = self.cli.get(key)
        if value:
            return True, value.decode('utf-8')
        return False, ""

    def set(self, key, value, expire):  # type: (str, str, int) -> None
        """
        storage key, value into the store, value has an expire time.(unit: second)
        """
        self.cli.set(key, value, ex=expire)


def test_config_with_memory_store(domain, app_settings):  # type: (str, AppSettings) -> Config
    return Config.new_config_with_memory_store(domain, app_settings, DefaultLogger(), LEVEL_DEBUG)


def test_config_with_redis_store(domain, app_settings):  # type: (str, AppSettings) -> Config
    return new_config_with_redis_store(domain, app_settings, DefaultLogger(), LEVEL_DEBUG)


def new_config_with_redis_store(domain, app_settings, logger,
                                log_level):  # type: (str, AppSettings, Logger, int) -> Config
    return Config.new_config(domain, app_settings, logger, log_level, RedisStore())

import os
import time
import pickle
import functools


class Cache:
    def __init__(self, directory="./cache", max_size=1023, default_ttl=60 * 60):
        self.directory = directory
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        if not os.path.exists(directory):
            os.makedirs(directory)

    def get(self, key):
        now = time.time()
        if key not in self.cache:
            return None
        value, timestamp, ttl = self.cache[key]
        if ttl is not None and now - timestamp > ttl:
            del self.cache[key]
            return None
        return pickle.loads(value)

    def set(self, key, value, ttl=None):
        now = time.time()
        if ttl is None:
            ttl = self.default_ttl
        value_data = pickle.dumps(value)
        self.cache[key] = (value_data, now, ttl)
        if len(self.cache) > self.max_size:
            self._evict()

    def __contains__(self, key):
        now = time.time()
        if key not in self.cache:
            return False
        value, timestamp, ttl = self.cache[key]
        if ttl is not None and now - timestamp > ttl:
            del self.cache[key]
            return False
        return True

    def _evict(self):
        if not self.cache:
            return
        oldest_key = min(self.cache, key=lambda x: self.cache[x][1])
        del self.cache[oldest_key]

    def clear(self):
        self.cache.clear()

    def __delitem__(self, key):
        del self.cache[key]
        cache_file = os.path.join(self.directory, f"{key}.pkl")
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def persist(self, key):
        if key not in self.cache:
            return
        value_data, timestamp, ttl = self.cache[key]
        if ttl is None:
            ttl = self.default_ttl
        cache_file = os.path.join(self.directory, f"{key}.pkl")
        with open(cache_file, "wb") as f:
            pickle.dump((value_data, timestamp, ttl), f)

    def load(self, key):
        cache_file = os.path.join(self.directory, f"{key}.pkl")
        if not os.path.exists(cache_file):
            return
        with open(cache_file, "rb") as f:
            value_data, timestamp, ttl = pickle.load(f)
            self.cache[key] = (value_data, timestamp, ttl)

    def __len__(self):
        return len(self.cache)

    def __iter__(self):
        return iter(self.cache)

    def __repr__(self):
        return f"Cache({len(self)}, max_size={self.max_size}, default_ttl={self.default_ttl})"


route_cache = Cache()


def cached(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        cache_key = f.__name__ + str(args) + str(kwargs)
        cached_result = route_cache.get(cache_key)
        if cached_result:
            return pickle.loads(cached_result)
        result = f(*args, **kwargs)
        route_cache.set(cache_key, pickle.dumps(result))
        return result

    return decorated_function

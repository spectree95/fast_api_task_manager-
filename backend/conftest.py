"""Configure pytest before importing the app; never use a developer's database."""

import os


os.environ.update({
    "DATABASE_URL": "sqlite://",
    "TEST_DATABASE_URL": "sqlite://",
    "REDIS_URL": "",
    "CACHE_TTL_SECONDS": "60",
    "CACHE_TASKS_KEY": "pytest-tasks",
    "SECRET_KEY": "isolated-tests-only-key-not-used-outside-this-process",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
})

#!/bin/bash

docker-compose exec backend \
python -m alembic upgrade head

docker-compose exec backend \
python -m cli seed-data

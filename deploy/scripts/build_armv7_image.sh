#!/usr/bin/env bash

docker buildx build \
  --platform linux/arm/v7 \
  --build-arg PANDAS_VERSION=2.2.3 \
  --build-arg PYTHON_VERSION=3.12 \
  -t meshbot-armv7-base:py3.12-pa2.2.3 \
  . --load

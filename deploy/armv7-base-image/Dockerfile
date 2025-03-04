ARG PYTHON_VERSION=3.12
ARG PANDAS_VERSION=2.2.3

FROM arm32v7/python:${PYTHON_VERSION}
ARG PANDAS_VERSION  # was reset after FROM

# Explicitly expand the variable inside RUN using shell substitution
RUN pip install "pandas==${PANDAS_VERSION}" "numpy==${PANDAS_VERSION}"

#!/usr/bin/env bash

python -m grpc_tools.protoc -I. --python_out=../app/grpc --pyi_out=../app/grpc --grpc_python_out=../app/grpc ./fetch.proto

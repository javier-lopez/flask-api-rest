#!/bin/sh

cd /usr/src/app/
pip install -r tests/requirements.txt
py.test


#!/bin/bash

screen -dm bash -c 'python3 ../../server/redirect.py; exec bash'

#!/bin/bash

find src/ -name "*.py" -exec cat {} \; | wc -l
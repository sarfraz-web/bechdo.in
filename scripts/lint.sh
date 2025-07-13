#!/bin/bash
set -e

echo "🔧 isort"
isort .

echo "🔧 black"
black .

echo "🔧 autoflake"
autoflake . --in-place --remove-all-unused-imports --remove-unused-variables --recursive

echo "🔧 autopep8"
autopep8 . --in-place --recursive --aggressive

echo "🕵️ pylint"
pylint $(git ls-files '*.py')

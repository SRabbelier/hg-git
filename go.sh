#!/bin/bash

git init && hg-blob-export.py $@ | git fast-import --export-marks=git.marks && join.py

#!/bin/bash

git init && hg-blob-export.py . | git fast-import --quiet --export-marks=git.marks && join.py && cp git-hg.marks .hg/git-mapfile

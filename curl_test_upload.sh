#!/bin/bash
# Correct curl command to test CSV upload API with multipart form data

curl -X POST "http://localhost:8000/api/data/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.csv"

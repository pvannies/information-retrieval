#!/bin/bash
case "$1" in
run)
  echo "================== Starting T2V with model =================="
  cat /model_name.txt
  echo "============================================================="
  echo
  uvicorn app:app --host 0.0.0.0 --port 8080
  ;;
model_name)
  cat /model_name.txt
  ;;
bash)
  /bin/bash
  ;;
esac
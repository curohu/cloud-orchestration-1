#! /usr/bin/bash

# this starts the gunicorn server and runs it as a daemon. It will log any app output into the script.out file. A tag has been added for easy process searching
nohup bash -c 'cd ./api-template/ && exec -a API-TEMPLATE python3 -m gunicorn api-template:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 ' > ./api-tempalte/script.out 2>&1 &

sleep 5s
# confirm all the processes are running
ps -aux | grep API-TEMPLATE

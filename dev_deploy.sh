#!/bin/bash

./build.sh
PROJECT=aqueous-choir-160420
gcloud -q --project=$PROJECT tasks queues create p1s1t6-firebase-replication

gcloud -q --project=$PROJECT app deploy --version 1 3>> upload_log.txt

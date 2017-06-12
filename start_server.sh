#!/usr/bin/env bash
docker build -t debrief .
docker run -d -p $1:5000 debrief
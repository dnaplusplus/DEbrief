#!/usr/bin/env bash
docker build -t debrief .
docker run -d -p 80:80 debrief
#!/bin/bash
set -e -x
apt-get update
PUBLIC_HOST_NAME=`curl http://169.254.169.254/latest/meta-data/public-hostname`
curl -H "Content-Type: application/json" -X POST 'http://ec2-23-20-211-255.compute-1.amazonaws.com:5000/register' -d '{"public_dns":"$PUBLIC_HOST_NAME"}'

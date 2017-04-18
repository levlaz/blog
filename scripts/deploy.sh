#!/bin/bash

ssh ubuntu@demo.levlaz.org 'docker pull levlaz/blog'
ssh ubuntu@demo.levlaz.org 'docker stop blog && docker rm blog'
ssh ubuntu@demo.levlaz.org 'docker run --name blog -d -p 80:5000 levlaz/blog'

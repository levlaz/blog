#!/bin/bash

scp docker-compose.yml ubuntu@demo.levlaz.org:/var/www/blog

ssh ubuntu@demo.levlaz.org 'cd /var/www/blog && docker-compose pull'
ssh ubuntu@demo.levlaz.org 'cd /var/www/blog && docker-compose build'
ssh ubuntu@demo.levlaz.org 'cd /var/www/blog && docker-compose up -d'

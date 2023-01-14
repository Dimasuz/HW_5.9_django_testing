#!/bin/bash
cd /home/dddd/django_cicd   # уточнить путь
git pull origin cicd
sudo systemctl restart gunicorn
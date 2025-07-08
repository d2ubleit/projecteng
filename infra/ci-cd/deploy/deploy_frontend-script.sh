#!/bin/bash

set -e
FRONTEND_DIR="/var/www/frontend"
SERVER_USER="user"
SERVER_IP="192.168.1.100"
BUILD_DIR="./dist"

echo "Building frontend..."
npm run build

echo "Copying files to server"
rsync -avz \
--delete \
--exclude='.env' \
-e ssh $BUILD_DIR/$SERVER_USER@SERVER_IP:$FRONTEDN_DIR

echo "Restarting nginx in process"
ssh $SERVER_USER@$SERVER_IP "sudo systemctl restar nginx"
echo "Deployment completed"

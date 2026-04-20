#!/bin/bash
# Mattermost Swarm Setup Script

set -e

PROJECT_DIR="$HOME/mattermost-swarm"

# --- Advanced Stack Management ---

echo "--- Stopping and Removing Old Stack ---"
# Remove the existing stack (ignore errors if it doesn't exist)
sudo docker stack rm mattermost || true

# Wait for services to be removed
echo "Waiting for stack cleanup..."
sleep 20

# 1. Create directory structure and set permissions
echo "Ensuring volumes and nginx directory structure..."
mkdir -p "$PROJECT_DIR/volumes/db/data"
mkdir -p "$PROJECT_DIR/volumes/app/config"
mkdir -p "$PROJECT_DIR/volumes/app/data"
mkdir -p "$PROJECT_DIR/volumes/app/logs"
mkdir -p "$PROJECT_DIR/volumes/app/plugins"
mkdir -p "$PROJECT_DIR/volumes/app/client/plugins"
mkdir -p "$PROJECT_DIR/volumes/app/bleve-indexes"
mkdir -p "$PROJECT_DIR/nginx/certs"
mkdir -p "$PROJECT_DIR/coturn"

echo "Setting permissions..."
sudo chown -R 2000:2000 "$PROJECT_DIR/volumes/app"
sudo chmod -R 777 "$PROJECT_DIR/volumes/db"

# 2. Generate certificates
if [ -f "$PROJECT_DIR/generate-certs.sh" ]; then
    echo "Generating/Updating SSL certificates..."
    bash "$PROJECT_DIR/generate-certs.sh"
fi

# 3. Deploy the new stack
echo "--- Deploying New Stack ---"
sudo docker stack deploy -c "$PROJECT_DIR/docker-stack.yml" mattermost

echo "--- Re-Setup Complete ---"
echo "Check your deployment with: sudo docker service ls"
echo ""
echo "--- Mattermost Calls ICE Servers Configuration ---"
echo "Paste this into System Console > Plugins > Calls > ICE Servers:"
echo ""
echo '[
  {
    "urls": ["stun:10.100.6.146:3478"]
  },
  {
    "urls": [
      "turn:10.100.6.146:3478?transport=udp",
      "turn:10.100.6.146:3478?transport=tcp"
    ],
    "username": "mmuser",
    "credential": "mmuser_turn_password_change_me"
  }
]'
echo ""

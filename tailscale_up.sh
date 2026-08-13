# 1. Reset existing funnel configs (if needed)
sudo tailscale funnel off

# 3. Route WebSocket event stream to Backend (8000)
sudo tailscale serve --bg --set-path /_event http://127.0.0.1:8000/_event

# 2. Proxy main web traffic to Frontend (3000)
sudo tailscale funnel --bg 3000 

# 4. Route upload and health-check routes to Backend (8000)
#sudo tailscale serve --bg --set-path /_upload http://127.0.0.1:8000/_upload
#sudo tailscale serve --bg --set-path /ping http://127.0.0.1:8000/ping
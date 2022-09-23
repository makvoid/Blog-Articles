# Interactive LED Strip (Server)
HTTP/HTTPS WebSocket server file for the interactive LED strip project.

## Installation / Start
```shell
yarn
node websocket-server.js
# Or, start the service
mv lighting-server.service /usr/lib/systemd/system
systemctl daemon-reload
# Add a non-root user (or use an existing User and update the service)
adduser webuser
systemctl start lighting-server.service && systemctl enable lighting-server.service
```

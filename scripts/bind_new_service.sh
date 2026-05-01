sudo cp /home/cnc/Dev/Team-303/scripts/start_software.service /etc/systemd/system/start_software.service

sudo systemctl daemon-reload
sudo systemctl enable start_software
For sending detections via secure tunnel in real time from either sagemic_local, or sagemic_stream if the
machine running inference is outside the SageBase network. 

1) Add public ssh key from sagebase machine out to either the pi running sagemic_local, or the 
remove VM running sagemic_stream, whatever machine detections are being stored in.

2) Create a group in the internal machine that only has write access to the specific directory
where detections will be transferred to, and create a user that is only within that group. The below command
will also move the python socket script to a new folder that sagepush user can access.

```
sudo groupadd -g <mount gid> sagebase-writers
sudo useradd --system --no-create-home --shell /usr/sbin/nologin -g sagebase-writers sagepush
sudo mkdir -p /opt/sagepush
sudo cp /home/<user>/sagemic/results_over_socket/recv_sagemic_socket.py /opt/sagepush/recv_sagemic_socket.py
sudo chown sagepush:sagebase-writers /opt/sagepush/recv_sagemic_socket.py
sudo chmod 640 /opt/sagepush/recv_sagemic_socket.py
```

*We mount a NAS to write to in our machine, and mount with the gid=sagebase-writers gid. If you are writing directly to
machine storage, simply change the sagebase-writer group to have write permissions to the desired folder:

```
sudo chgrp sagebase-writers /path/to/directory
sudo chmod 770 -R /path/to/directory
```

3) Edit sagemic_tunnel.service and recv_sagemic.service on the internal machine and copy them to systemd: 

```
sudo cp sagemic_tunnel.service /etc/systemd/service/sagemic_tunnel.service
sudo cp recv_sagemic.service /etc/systemd/service/recv_sagemic.service
```

```
sudo systemctl daemon-reload
sudo systemctl start sagemic_tunnel.service
sudo systemctl start recv_sagemic.service
```

Ensure the port is working by checking the status of the systemd or checking what ports are listening
on the machine:

```
ss -tulpen
```

or

```
sudo lsof -i tcp
```

Ensure both services are running with:

```
sudo systemctl status <service>
```


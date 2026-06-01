### So, you want your custom IoT (non-LoRa) devices to send their data to your database in real time, from anywhere in the field?

## Setting up your VM
We use an Ubuntu 26 image in a virtual machine, and only enable ingress from port 22 to start, ideally only from the IP you
will be SSHing in from. We will enable ingress and egress from port 8883 later, but for now just SSH access is needed.

## TBMQ (ThingsBoard MQTT Broker)
[TBMQ Setup Guide](https://thingsboard.io/docs/mqtt-broker/installation/docker/)

The link describes the steps to setup the TBMQ Broker in a Docker container.
In order to view the Broker in your laptop browser from the VM, ensure you port forward to 8080 on your
machine so you can access the UI from localhost:8080. 

```
ssh -L 8080:localhost:8080 user@host
```

## Enabling TLS
In order to enable one-way TLS, you need to generate a self-signed certificate root. It's recommended to create
an intermediate key as well, but for the purpose of simplicity in this demo we will describe the making a root certificate,
and a server certificate. 

In a secure machine (not the virtual machine running TBMQ) create a root certificate:
```
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout rootCA.key -out rootCA.pem
```

FIll in the details as needed. You should have a rootCA.key and a rootCA.pem. The rootCA.key NEVER leaves the machine
or gets shared elsewhere. Best practice is to keep it air-gapped or on a piece of designated storage media.

Then create a private key for the TBMQ server:
```
openssl genrsa -out server.key 2048
```

Then create a certificate signing request from the server.key:
```
openssl req -new -key server.key -out server.csr
```

Fill in the details as needed. Password is optional, if you choose to use one you will need it in the TBMQ docker file later.
Then sign the certificate request with the rootCA, this WILL expire eventually so you need to set up a mechanism to rotate.

```
openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 365 -sha256
Certificate request self-signature ok
```

Then put the server certificate and key into a singular .pem file. 

```
cat server.crt server.key > server.pem
```

Copy the server.pem and server.key into a folder in /home/user/certs into the TBMQ machine. 

Copy the rootCA.pem onto the end-device in a similar /certs folder, as well as onto the Node-Red machine. 

What we have created is a way to do one-way TLS, wherein the server gets authenticated by the publishers and subscribers, 
ensuring that they are transmitting encrypted data to the correct MQTT broker, the rootca is able to encode/decode the messages. 

# Further hardening
Best practices would be to NOT self-sign, and to obtain a rootCA from an actual certificate authority, it will also involve doing
two way TLS, which will remove the need for pub/sub usernames and passwords later. But one thing at a time!

## Modifying the docker-compose.yml

Once the example broker has been set-up, we need to add in our TLS settings and increase our max data rate in the docker-compose.yml

```
docker compose stop <container id>
```

In the compose file, add these lines to the 'tbmq' portion:

```
      SECURITY_MQTT_BASIC_ENABLED: "true"
      LISTENER_SSL_BIND_PORT: "8883"

      SSL_NETTY_MAX_PAYLOAD_SIZE: 600000
      TCP_NETTY_MAX_PAYLOAD_SIZE: 600000

      LISTENER_SSL_ENABLED: "true"
      LISTENER_SSL_CREDENTIALS_TYPE: "PEM"
      LISTENER_SSL_PEM_CERT: "/config/certificates/server.pem"
      LISTENER_SSL_PEM_KEY: "/config/certificates/server.key"
      LISTENER_SSL_PEM_KEY_PASSWORD: ""
```

Also ensure that under the 'ports' portion of the tbmq lines have a mapping for 8883:8883

Re-run the tbmq-install-and-run bash script in the folder.

You may need to toggle the enable x.509 auth toggle in the main TBMQ UI once you re-navigate to the front-end. 

## Ports
Now that TLS is enabled on 8883, you can open that port within the Security Groups on the virtual host managing platform. 

## Pub/Sub

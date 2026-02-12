## So, you want your LoRa devices to post their data to your SageBase database and frontend. What now?
 
You will need:

	- A LoRa Server
	- Node-Red

Which LoRa server should you choose?
| Server | Cost | Set-up difficulty | Connectivity Constraints |
| --- | --- | --- | --- |
| Chirpstack | Free | Moderate | Needs to be run on a machine where port 1700 can be opened only IF cell gateways will be used |
|The Things Network | Limited Free, high cost to scale | Super Easy | Gateways need internet connectivity and downstream database also needs internet access |

## If Chirpstack- where should you host it?

*For TTN, this section can be ignored as the data will be accessible wherever
you have internet. 

For a local setup, Chirpstack can be run on any machine within your local network.
IE, if all your gateways have an ip address that is on the same subnet as your chirpstack server.

If you have any cell enabled gateways, or gateways connected to any internet
that is not within your chirpstack server network, you will need port 1700 open for ingress on the machine hosting chirpstack. 

If that is not possible on your local network for security reasons, host chirpstack on a remote machine where this
port opening is possible, such as a virtual machine. 
 
### Hosting Chirpstack
We choose to host Chirpstack via Docker on an ubuntu machine, instructions found here:
https://www.chirpstack.io/docs/getting-started/docker.html

As noted in the docs, the default region is EU 868. For USA, the region needs to be US 915. This amounts to changing
the docker-compose.yml file under chirpstack-gateway-bridge environment variables to the below:
'''
    environment:
      - INTEGRATION__MQTT__EVENT_TOPIC_TEMPLATE=us915_0/gateway/{{ .GatewayID }}/event/{{ .EventType }}
      - INTEGRATION__MQTT__STATE_TOPIC_TEMPLATE=us915_0/gateway/{{ .GatewayID }}/state/{{ .StateType }}
      - INTEGRATION__MQTT__COMMAND_TOPIC_TEMPLATE=us915_0/gateway/{{ .GatewayID }}/command/#
'''
#### Cell-enabled Gateways
If you have any cell enabled gateways, or gateways that live outside the local network that Chirpstack is hosted on, IE on
a Starlink wifi or elsewhere, you will need to open port 1700 for ingress. We use UDP for data transmission from the gateways, 
and Chirpstack will not see data from these gateways unless it can listen on that port without a firewall. 

#### Configuring the Gateways
We typically use RAK brand gateways, and their configuration page allows you to input the address of the LoRa server it should
forward data to. If hosted locally, merely input the IP address on the local network of the machine running chirpstack. If hosted
externally, you need the public static ip of the server.

*TTN has a string type of server name for data forwarding, and that can be found on your instance, this would go in place of
the ip address that chirpstack uses.

# Node-Red
Node-Red is the data handler for incoming LoRa data where you can decide where and how the payloads arrive at other
end points, and in our case, SageBase.
Again, we use Docker set-ups, here is the link to the basic Node-Red docker install: https://nodered.org/docs/getting-started/local#installing-with-docker

And there is an additional page with more parameters to customize the instance, we recommend ensuring you have a persistent
data volume storage mount to ensure the Node-Red data persists across reboots and restarts, the default is a test bed
that doesn't save your changes across restarts. https://nodered.org/docs/getting-started/docker

You can also add a username or password to increase security (found in the settings.js file within the nodered data directory,
as Node-Red will be available on the ip:1880 port of the machine its hosted on. Speaking of hosting...

You can use our node-red docker-compose file found here so that the future instructions are easier to follow.

## Where to host Node-Red
You can host Node-Red on the same machine that SageBase is located. This may or may not be where Chirpstack is hosted.

### Linking Chirpstack with Node-Red
Follow the instuctions here to install the chirpstack package into Node-Red, allowing for easy receiving and handling of uplink
payloads from devices: https://www.chirpstack.io/docs/guides/node-red-integration.html

You can use the example Node-Red json provided in this repo to get started with the flow that we use to grab temperature sensor
data from chirpstack (Dragino LHT65N), and post it to the database. You will need to make a few tweaks to work with your system, namely:

- MQTT Broker Node
- MQTT in node
- Device Switch Node

For the MQTT broker node, you mainly need to input the ip address of your Chirpstack MQTT broker. If they are on the same internal
network, it will just be the ip address of the machine its running on in that network.

#### Finding the IP address to input in Node-Red for MQQT Broker if Chirpstack is hosted on a remote Docker. 
You will need to create a tunnel on the remote machine to  

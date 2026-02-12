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


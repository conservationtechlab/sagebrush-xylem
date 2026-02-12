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

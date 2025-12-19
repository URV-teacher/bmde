# cloner
Clones Git repos from the private servers of the DEIM

./src/connect_fortivpn.exp $(cat ./secrets/VPN_PROFILE) $(cat ./secrets/VPN_PASSWORD)

 ./src/configure_fortivpn.exp $(cat ./secrets/VPN_PROFILE) $(cat ./secrets/VPN_GATEWAY) $(cat ./secrets/VPN_USER)

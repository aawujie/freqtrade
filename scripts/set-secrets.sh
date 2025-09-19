export PUBLIC_IP_ADDRESS=$(ipconfig getifaddr $(route -n get default | awk '/interface:/{print $2}'))
export LISTEN_PORT=8080

echo "--------------------------------"
echo "Secret Environment Variables:"
echo "--------------------------------"
echo "web url: http://$PUBLIC_IP_ADDRESS:$LISTEN_PORT"
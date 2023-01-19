screen -X -S MyHomeParser quit
screen -dmS MyHomeParser
sleep 1
screen -r MyHomeParser -X stuff 'source /root/Projects/GEparsBot/bin/activate
'
sleep 1
screen -r MyHomeParser -X stuff 'cd /root/Projects/GEparsBot/RentApartmentGE
'
sleep 1
screen -r MyHomeParser -X stuff 'python MyHomeParseJSON.py
'
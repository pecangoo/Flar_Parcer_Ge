screen -X -S AdminBot quit
screen -dmS AdminBot
sleep 1
screen -r AdminBot -X stuff 'source /root/Projects/GEparsBot/bin/activate
'
sleep 1
screen -r AdminBot -X stuff 'cd /root/Projects/GEparsBot/RentApartmentGE
'
sleep 1
screen -r AdminBot -X stuff 'python adminBot.py
'
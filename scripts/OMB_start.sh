screen -X -S MenuBot quit
screen -dmS MenuBot
sleep 1
screen -r MenuBot -X stuff 'source /root/Projects/GEparsBot/bin/activate
'
sleep 1
screen -r MenuBot -X stuff 'cd /root/Projects/GEparsBot/RentApartmentGE
'
sleep 1
screen -r MenuBot -X stuff 'python botMenu.py
'
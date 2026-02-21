"""
Written by: Riley Foxton
Date: 21/2/2026
Contact for records if wanted
"""
import json
import requests
from datetime import datetime

API_MAX =  31

#Loading last update date and the base url (private file)
with open("record.json", "r") as record:
    record = json.load(record)

#Loading all previous songs (private file)
with open("record_songs.json", "r") as song_record:
    song_record = json.load(song_record)

#getting Station name
stationName = record["station_name"]
#Setting up request
baseurl = record["baseurl"]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

#Finding last known date
last_updated = datetime(record["last_updated"]["year"], record["last_updated"]["month"], record["last_updated"]["day"], 0, 0, 0)
current = datetime.now()
difference = current-last_updated
days_since = min(difference.days, API_MAX)

#update for all previous days including today since last update
while days_since >= 0:
    #get the days songs
    url = baseurl+"?day="+str(days_since)+"&playerID=778"
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    dateday = data["data"]["startDate"].split()[0]

    #for each song in that day
    for current_song in data["data"]["songs"]:
        #remove unwanted information
        current_song.pop("itunes_img")
        current_song.pop("itunes_url")
        current_song.pop("image")
        current_song.pop("time_ago")
        current_song.pop("upvotes")
        current_song.pop("downvotes")
        current_song.pop("locale_time")

        #see if the song exists in records
        archiveSong = song_record.get(str(current_song["song_id"])+"-"+str(current_song["song_name"]), None)
        if archiveSong == None:
            #if it doesnt exist make it, key must be formated like this as there is ocassion the song_id is null and song_name is not always unique
            song_record[str(current_song["song_id"])+"-"+str(current_song["song_name"])] = current_song
        elif archiveSong["last_played"] < current_song["last_played"]:
            #if it does exist update the last played date (unix time)
            archiveSong["last_played"] = current_song["last_played"]
    
    #write a file with the days information
    with open(stationName+"-"+dateday+".json", "w") as file:
        file.write(json.dumps(data, indent=4))
    
    days_since -= 1

last_updated = {"last_updated":{"day": current.day, "month": current.month, "year": current.year}, "baseurl": baseurl, "station_name": stationName}

#update the record to note the last update
with open("record_songs.json", "w") as record:
    record.write(json.dumps(song_record, indent=4))

#update the master song list
with open("record.json", "w") as record:
    record.write(json.dumps(last_updated, indent=4))

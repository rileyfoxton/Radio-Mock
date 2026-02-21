import json
import requests
from datetime import timedelta, datetime

API_MAX =  31
# Let's say this is the URL you found in your network tab
url = "https://www.live885.com/api/v1/music/broadcastHistory?day=0&playerID=778"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

with open("record.json", "r") as record:
    record = json.load(record)

with open("record_songs.json", "r") as song_record:
    song_record = json.load(song_record)

last_updated = datetime(record["last_updated"]["year"], record["last_updated"]["month"], record["last_updated"]["day"], 0, 0, 0)
current = datetime.now()
difference = current-last_updated

days_since = min(difference.days, API_MAX)

while days_since >= 0:
    url = "https://www.live885.com/api/v1/music/broadcastHistory?day="+str(days_since)+"&playerID=778"

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    dateday = data["data"]["startDate"].split()[0]

    for song in data["data"]["songs"]:
        song.pop("itunes_img")
        song.pop("itunes_url")
        song.pop("image")
        song.pop("time_ago")
        song.pop("upvotes")
        song.pop("downvotes")
        song.pop("locale_time")

        if song_record.get(str(song["song_id"])+"-"+str(song["song_name"]), None) == None:
            song_record[str(song["song_id"])+"-"+str(song["song_name"])] = song

    with open("live885-"+dateday+".json", "w") as file:
        file.write(json.dumps(data, indent=4))
    
    days_since -= 1

last_updated = {"day": current.day, "month": current.month, "year": current.year}
last_updated = {"last_updated": last_updated}

with open("record_songs.json", "w") as record:
    record.write(json.dumps(song_record, indent=4))

with open("record.json", "w") as record:
    record.write(json.dumps(last_updated, indent=4))

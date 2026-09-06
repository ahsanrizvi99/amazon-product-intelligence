import json
import csv

with open('free4talk_data.json', 'r', encoding='utf-8') as file:
    response = json.load(file)

extracted_users = {}

for room_id, room_data in response.get("data", {}).items():
    for client in room_data.get("clients", []):
        user_id = client.get("id")
        if user_id not in extracted_users:
            extracted_users[user_id] = {
                "id": user_id,
                "name": client.get("name"),
                "avatar": client.get("avatar"),
                "followers": client.get("followers", 0),
                "following": client.get("following", 0),
                "friends": client.get("friends", 0),
                "role": "client",
                "isVerified": False
            }
            
    creator = room_data.get("creator", {})
    creator_id = creator.get("id")
    if creator_id and creator_id not in extracted_users:
        extracted_users[creator_id] = {
            "id": creator_id,
            "name": creator.get("name"),
            "avatar": creator.get("avatar"),
            "followers": 0, 
            "following": 0,
            "friends": 0,
            "role": "creator",
            "isVerified": creator.get("isVerified", False)
        }

all_users = list(extracted_users.values())

if all_users:
    # Define the CSV headers
    headers = ["id", "name", "avatar", "followers", "following", "friends", "role", "isVerified"]
    
    with open("free4talk_users.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_users)
        
    print(f"Successfully exported {len(all_users)} users to free4talk_users.csv")
from flask import Flask, jsonify
import aiohttp
import asyncio
import requests
from byte import *
from protobuf_parser import Parser, Utils

app = Flask(__name__)

def fetch_tokens():
    url = "http://82.25.118.49:5001/token"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            tokens_data = response.json()
            print("🔹 Data retrieved from API:", tokens_data)

            if isinstance(tokens_data, dict) and "tokens" in tokens_data:
                tokens = tokens_data["tokens"]
            elif isinstance(tokens_data, list):
                tokens = []
                for item in tokens_data:
                    if isinstance(item, dict) and "tokens" in item:
                        tokens.extend(item["tokens"])
            else:
                tokens = []

            valid_tokens = [t for t in tokens if t and t != "N/A"][:4]

            print(f"✅ Extracted {len(valid_tokens)} valid tokens: {valid_tokens}")
            return valid_tokens
        else:
            print(f"⚠️ Failed to fetch tokens. Response code: {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Error while fetching tokens: {e}")
        return []

async def visit(session, token, uid, data):
    url = "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
    headers = {
        "ReleaseVersion": "OB49",
        "X-GA": "v1 1",
        "Authorization": f"Bearer {token}",
        "Host": "clientbp.ggblueshark.com"
    }
    try:
        async with session.post(url, headers=headers, data=data, ssl=False):
            pass
    except:
        pass

async def send_requests_concurrently(tokens, uid, num_requests=300):
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        data = bytes.fromhex(encrypt_api("08" + Encrypt_ID(uid) + "1801"))
        tasks = [asyncio.create_task(visit(session, tokens[i % len(tokens)], uid, data)) for i in range(num_requests)]
        await asyncio.gather(*tasks)

@app.route('/<int:uid>', methods=['GET'])
def send_visits(uid):
    tokens = fetch_tokens()
    
    if not tokens:
        return jsonify({"message": "⚠️ No valid tokens found"}), 500
    
    print(f"✅ Available tokens: {len(tokens)}")

    num_requests = 300
    asyncio.run(send_requests_concurrently(tokens, uid, num_requests))

    return jsonify({"message": f"✅ Sent {num_requests} visits to UID: {uid} using {len(tokens)} tokens at high speed"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50099)
import json
import hmac
import hashlib
import requests
import config

def send_webhook(new_opportunities):
    if not config.WEBHOOK_URL or not new_opportunities:
        return
    
    payload = json.dumps([
        {
            "id": opp.id,
            "title": opp.title,
            "type": opp.type,
            "source_link": opp.source_link,
            "source_name": opp.source_name,
        } for opp in new_opportunities
    ]).encode('utf-8')
    
    headers = {"Content-Type": "application/json"}
    if config.WEBHOOK_SECRET:
        signature = hmac.new(
            config.WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        headers["X-Webhook-Signature"] = f"sha256={signature}"
        
    try:
        requests.post(config.WEBHOOK_URL, data=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Webhook failed: {e}")

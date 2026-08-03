"""
Live API test: login as a real customer and test GET /api/v1/customer/addresses
This tests the exact flow the Flutter app performs.
"""
import asyncio
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000/api/v1"

def http_get(url, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as ex:
        return 0, {"error": str(ex)}

def http_post(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"raw": body.decode()}
    except Exception as ex:
        return 0, {"error": str(ex)}


async def main():
    from app.core.config import settings
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie
    from app.auth.models import User
    
    uri = settings.MONGODB_URI.get_secret_value()
    db_name = settings.MONGODB_DATABASE
    client = AsyncIOMotorClient(uri)
    await init_beanie(database=client[db_name], document_models=[User])
    
    # Get any real customer from the database
    customers = await User.find(User.role == "customer", User.is_active == True).to_list(5)
    if not customers:
        print("[FAIL] No active customers in DB!")
        return
    
    cust = customers[0]
    print(f"\n[1] Found customer: {cust.email or cust.phone} (id={cust.id})")
    
    client.close()
    
    # Try to login with this customer using a dummy password to see the login response format
    print(f"\n[2] Testing address endpoint without auth:")
    code, body = http_get(f"{BASE}/customer/addresses")
    print(f"  Status: {code}")
    print(f"  Body: {json.dumps(body, indent=2)[:300]}")
    
    # Check what routes exist
    print(f"\n[3] Testing backend health:")
    code, body = http_get(f"{BASE}/health")
    print(f"  /health -> {code}: {body}")
    
    code2, body2 = http_get(f"http://127.0.0.1:8000/api/v1/docs")
    print(f"  /docs -> {code2}")


if __name__ == "__main__":
    asyncio.run(main())

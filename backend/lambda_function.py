import base64, hashlib, hmac, json, math, os, time, urllib.request, uuid, boto3
from boto3.dynamodb.conditions import Attr
T = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
HERE = os.path.dirname(os.path.abspath(__file__))
STEP_SECONDS = 25  # demo speed: preparing -> on the way -> delivered
_d = open(os.path.join(HERE, "data.js"), encoding="utf-8").read()
MENU = {r["n"]: r for r in json.loads(_d[_d.index("["):_d.rindex("]") + 1])}

SQS = boto3.client("sqs") if os.environ.get("QUEUE_URL") else None
def enqueue(oid):  # hand the confirmed order to the SQS queue (worker Lambda picks it up)
    try:
        if SQS: SQS.send_message(QueueUrl=os.environ["QUEUE_URL"], MessageBody=json.dumps({"orderId": oid}))
    except Exception as e: print("enqueue failed", e)

class V(Exception): pass
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type,authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}
def resp(code, body, ctype="application/json"):
    return {"statusCode": code, "headers": {"Content-Type": ctype, **CORS}, "body": body if isinstance(body, str) else json.dumps(body, default=str)}
rnd = lambda x: int(math.floor(x + 0.5))
def b64(b): return base64.urlsafe_b64encode(b).decode().rstrip("=")
def sign(s):
    k = os.environ.get("AUTH_SECRET")
    if not k: raise V("Server setup missing: add the AUTH_SECRET environment variable")
    return b64(hmac.new(k.encode(), s.encode(), hashlib.sha256).digest())
def make_token(phone): p = b64(json.dumps({"p": phone, "e": int(time.time()) + 7 * 86400}).encode()); return p + "." + sign(p)
def who(hdr):
    a = hdr.get("authorization", "")
    if not a.startswith("Bearer ") or "." not in a: return None
    p, s = a[7:].rsplit(".", 1)
    if not hmac.compare_digest(s, sign(p)): return None
    d = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
    return d["p"] if d["e"] > time.time() else None
def hpw(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100000).hex()

def price(b):
    r = MENU.get(b.get("restaurant"))
    if not r: raise V("Unknown restaurant")
    mode = "pickup" if b.get("mode") == "pickup" else "delivery"; items, sub = [], 0
    for it in b.get("items") or []:
        d = next((m for m in r["m"] if m[0] == it.get("name")), None); q = it.get("qty")
        if not d or not isinstance(q, int) or not 1 <= q <= 20: raise V("Invalid item in cart")
        items.append({"name": d[0], "price": d[1], "qty": q}); sub += d[1] * q
    if not items: raise V("Cart is empty")
    p = r["p"]; disc = min(p[1], rnd(sub * p[0] / 100)) if p and sub >= p[2] else 0
    tax = rnd((sub - disc) * .05); fee = 0 if mode == "pickup" else r["fee"]
    return r, mode, items, disc, sub - disc + tax + fee

def rzp_on(): return bool(os.environ.get("RAZORPAY_KEY_ID") and os.environ.get("RAZORPAY_KEY_SECRET"))
def rzp(path, payload):
    k = base64.b64encode((os.environ["RAZORPAY_KEY_ID"] + ":" + os.environ["RAZORPAY_KEY_SECRET"]).encode()).decode()
    q = urllib.request.Request("https://api.razorpay.com/v1/" + path, json.dumps(payload).encode(), {"Content-Type": "application/json", "Authorization": "Basic " + k})
    return json.load(urllib.request.urlopen(q, timeout=8))

def status(it):
    pend = it["paymentStatus"] == "PENDING"
    step = -1 if pend else min(3, int((time.time() - float(it.get("paidAt") or it["createdAt"])) // STEP_SECONDS))
    return {"orderId": it["orderId"], "restaurant": it["restaurant"], "total": it["total"], "mode": it["mode"], "step": step,
            "payment": it["paymentStatus"], "payMode": "razorpay" if rzp_on() else "demo", "createdAt": it["createdAt"]}
def get_order(oid):
    it = T.get_item(Key={"orderId": oid}).get("Item")
    if not it or oid.startswith("USER#"): raise V("Order not found")
    return it

def lambda_handler(event, context):
    h = event.get("requestContext", {}).get("http", {}); m = h.get("method", "GET")
    p = event.get("rawPath", "/").rstrip("/") or "/"; hdr = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if m == "OPTIONS":  # browser permission check from another site (e.g. the S3 page)
        return {"statusCode": 204, "headers": CORS, "body": ""}
    try:
        if m == "GET" and p == "/":
            html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read().replace('window.API_URL = "";', 'window.API_URL = "auto";')
            return resp(200, html, "text/html; charset=utf-8")
        b = json.loads(event.get("body") or "{}") if m == "POST" else {}
        if p in ("/auth/signup", "/auth/login") and m == "POST":
            ph, pw, nm = str(b.get("phone", "")), str(b.get("password", "")), str(b.get("name", "")).strip()[:60]
            if not (ph.isdigit() and len(ph) == 10) or len(pw) < 6: raise V("Enter a 10-digit phone and a password of 6+ characters")
            key = {"orderId": "USER#" + ph}; u = T.get_item(Key=key).get("Item")
            if p.endswith("signup"):
                if u: raise V("This phone number already has an account. Sign in instead.")
                if not nm: raise V("Enter your name")
                salt = os.urandom(16); u = {**key, "name": nm, "salt": salt.hex(), "hash": hpw(pw, salt), "createdAt": int(time.time())}; T.put_item(Item=u)
            elif not u or not hmac.compare_digest(u["hash"], hpw(pw, bytes.fromhex(u["salt"]))): raise V("Wrong phone number or password")
            return resp(200, {"token": make_token(ph), "user": {"name": u["name"], "phone": ph}})
        if p == "/me/orders" and m == "GET":
            ph = who(hdr)
            if not ph: return resp(401, {"error": "Please sign in"})
            kw, rows = {"FilterExpression": Attr("userId").eq(ph)}, []
            while True:
                r = T.scan(**kw); rows += r["Items"]
                if "LastEvaluatedKey" not in r: break
                kw["ExclusiveStartKey"] = r["LastEvaluatedKey"]
            rows.sort(key=lambda x: -float(x["createdAt"]))
            return resp(200, {"orders": [{**status(x), "id": x["orderId"]} for x in rows[:30]]})
        if p == "/orders" and m == "POST":
            c = b.get("customer") or {}; ph = str(c.get("phone", "")); r, mode, items, disc, total = price(b)
            if not (ph.isdigit() and len(ph) == 10) or not str(c.get("name", "")).strip(): raise V("Name and a 10-digit phone are required")
            addr = "Pickup" if mode == "pickup" else str(c.get("address", "")).strip()[:200]
            if not addr: raise V("Delivery address is required")
            online = b.get("payment") == "Online"; oid = "DP" + uuid.uuid4().hex[:8].upper(); now = int(time.time())
            T.put_item(Item={"orderId": oid, "createdAt": now, "restaurant": r["n"], "mode": mode, "payment": "Online" if online else "Cash",
                "paymentStatus": "PENDING" if online else "COD", "items": items, "discount": disc, "total": total, "userId": who(hdr) if hdr.get("authorization") else "",
                "customer": {"name": str(c["name"]).strip()[:60], "phone": ph, "address": addr}})
            if not online: enqueue(oid)  # cash orders are confirmed now; online orders after payment
            return resp(200, {"orderId": oid, "total": total, "paymentStatus": "PENDING" if online else "COD", "payMode": "razorpay" if rzp_on() else "demo"})
        if p.startswith("/orders/") and m == "GET": return resp(200, status(get_order(p.split("/")[2])))
        if p == "/pay/create" and m == "POST":
            it = get_order(str(b.get("orderId")))
            if it["paymentStatus"] != "PENDING": raise V("This order is already paid")
            if not rzp_on(): return resp(200, {"mode": "demo"})
            o = rzp("orders", {"amount": int(it["total"]) * 100, "currency": "INR", "receipt": it["orderId"]})
            T.update_item(Key={"orderId": it["orderId"]}, UpdateExpression="SET rzpOrderId=:r", ExpressionAttributeValues={":r": o["id"]})
            return resp(200, {"mode": "razorpay", "key": os.environ["RAZORPAY_KEY_ID"], "rzpOrderId": o["id"], "amount": o["amount"]})
        if p == "/pay/verify" and m == "POST":
            it = get_order(str(b.get("orderId")))
            if it["paymentStatus"] != "PENDING": raise V("This order is already paid")
            if rzp_on():
                good = hmac.new(os.environ["RAZORPAY_KEY_SECRET"].encode(), (it.get("rzpOrderId", "") + "|" + str(b.get("razorpay_payment_id"))).encode(), hashlib.sha256).hexdigest()
                if not it.get("rzpOrderId") or not hmac.compare_digest(good, str(b.get("razorpay_signature"))): raise V("Payment could not be verified")
                pid = str(b["razorpay_payment_id"])
            elif b.get("demo"): pid = "demo"
            else: raise V("Payment could not be verified")
            T.update_item(Key={"orderId": it["orderId"]}, UpdateExpression="SET paymentStatus=:s, paidAt=:t, paymentId=:p",
                          ExpressionAttributeValues={":s": "PAID", ":t": int(time.time()), ":p": pid})
            enqueue(it["orderId"])
            return resp(200, {"ok": True})
        return resp(404, {"error": "Not found"})
    except V as e: return resp(400, {"error": str(e)})
    except Exception as e: return resp(500, {"error": "Something went wrong. Please try again."})

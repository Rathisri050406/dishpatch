import json, os, time, uuid, boto3
from decimal import Decimal
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
STEP_SECONDS = 25  # demo speed: placed -> cooking -> on the way -> delivered

def resp(code, body):
    return {"statusCode": code, "body": json.dumps(body, default=str)}

def lambda_handler(event, context):
    http = event.get("requestContext", {}).get("http", {})
    try:
        if http.get("method") == "GET":
            item = table.get_item(Key={"orderId": event["pathParameters"]["id"]}).get("Item")
            if not item:
                return resp(404, {"error": "Order not found"})
            step = min(3, int((time.time() - float(item["createdAt"])) // STEP_SECONDS))
            return resp(200, {"orderId": item["orderId"], "step": step})
        o = json.loads(event.get("body") or "{}", parse_float=Decimal)
        if not o.get("items") or not o.get("customer", {}).get("phone"):
            return resp(400, {"error": "Order needs items and a phone number"})
        oid = "TE" + uuid.uuid4().hex[:8].upper()
        table.put_item(Item={**o, "orderId": oid, "createdAt": int(time.time())})
        return resp(200, {"orderId": oid})
    except Exception as e:
        return resp(500, {"error": str(e)})

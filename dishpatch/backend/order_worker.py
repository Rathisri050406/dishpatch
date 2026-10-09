"""Worker Lambda. Trigger: SQS queue. Handler name: order_worker.handler
For each queued order: mark it CONFIRMED in DynamoDB, then publish an 'OrderPlaced' event to EventBridge."""
import json, os, time, boto3
T = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
EB = boto3.client("events")

def handler(event, context):
    for rec in event["Records"]:
        oid = json.loads(rec["body"])["orderId"]
        it = T.get_item(Key={"orderId": oid}).get("Item")
        if not it:
            continue
        T.update_item(Key={"orderId": oid}, UpdateExpression="SET kitchenStatus=:k, confirmedAt=:t",
                      ExpressionAttributeValues={":k": "CONFIRMED", ":t": int(time.time())})
        EB.put_events(Entries=[{"Source": "dishpatch.orders", "DetailType": "OrderPlaced",
            "Detail": json.dumps({"orderId": oid, "restaurant": it["restaurant"], "total": int(it["total"]), "payment": it["payment"], "mode": it["mode"]})}])
    return {"processed": len(event["Records"])}

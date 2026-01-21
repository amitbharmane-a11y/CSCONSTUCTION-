import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import db_cursor
import json

def handler(request):
    """Health check endpoint"""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1 as health_check")
            result = cur.fetchone()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "ok", "database": "connected"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "message": str(e)})
        }
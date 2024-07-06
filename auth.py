import os
from dotenv import load_dotenv
from yoomoney import Authorize

load_dotenv()
YOOMONEY_CLIENT_ID = os.getenv('YOOMONEY_CLIENT_ID')

Authorize(
      client_id=YOOMONEY_CLIENT_ID,
      redirect_uri="https://t.me/my_test2_bot",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )



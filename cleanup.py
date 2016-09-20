from os import getenv
from twilio.rest import TwilioRestClient

SID = getenv("TWILIO_SID")
TOKEN = getenv("TWILIO_TOKEN")


if __name__ == "__main__":
    if SID == None or TOKEN == None:
        print("fix your env vars")
        exit(1)

    twilio = TwilioRestClient(SID, TOKEN)

    calls = twilio.calls.list()

    for call in calls:
        call.delete()

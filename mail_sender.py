from mailjet_rest import Client

from django.conf import settings


def send_mail_from_mailjet(
        to_addr,
        to_name,
        subject,
        content,
):
    mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.FROM_EMAIL,
                    "Name": "FreshBite",
                },
                "To": [
                    {
                        "Email": to_addr,
                        "Name": to_name,
                    }
                ],
                "Subject": subject,
                "TextPart": content,
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())

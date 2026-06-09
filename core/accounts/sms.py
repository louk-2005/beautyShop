import requests
from django.conf import settings


def send_otp(phone_number, code):
    """
    ارسال کد تایید (OTP) با استفاده از کاوه نگار
    """

    try:
        url = (
            f"https://api.kavenegar.com/v1/"
            f"{settings.KAVENEGAR_API_KEY}/sms/send.json"
        )

        payload = {
            "receptor": phone_number,
            "sender": settings.SMS_SENDER_NUMBER,
            "message": f"کد تایید شما: {code}",
        }

        response = requests.post(
            url,
            data=payload,
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            if result.get("return", {}).get("status") == 200:
                return True

            print(
                "Kavenegar Error:",
                result
            )

            return False

        print(
            f"HTTP Error {response.status_code}: "
            f"{response.text}"
        )

        return False

    except requests.exceptions.RequestException as exc:

        print(
            f"Request Error while sending OTP: {exc}"
        )

        return False
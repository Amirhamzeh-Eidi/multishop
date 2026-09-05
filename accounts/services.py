from .models import Otp
from  django.utils import timezone
from datetime import timedelta
from random import randint
class ExpiredOtpError(Exception):
    pass
class ToManyAttemptsError(Exception):
    pass
class WrongOtpError(Exception):
    pass
class InvalidOtpError(Exception):
    pass

class OtpRequestToSoon(Exception):
    pass
class OtpShortTermLimitExceeded(Exception):
    pass
class OtpDailyLimitExceeded(Exception):
    pass
class OtpService():
    def verify(token, code):
        try:
            otp = Otp.objects.get(token=token, code=code, active=True)
            if timezone.now() > otp.expires_at:
                raise ExpiredOtpError()
        except Otp.DoesNotExist:
            try:
                otp = Otp.objects.get(token=token, active=True)
                if otp.attempts >= 5:
                    otp.active = False
                    otp.save()
                    raise ToManyAttemptsError()
                otp.attempts += 1
                otp.save()
                raise WrongOtpError()
            except Otp.DoesNotExist:
                raise InvalidOtpError()
        return otp

    def resend_otp(token):
        try:
            otp = Otp.objects.get(token=token)
            otps = Otp.objects.filter(identifier=otp.identifier)
            count_10_min = 0
            count_24_hours = 0
            for item in otps:
                if item.created_at > timezone.now() - timedelta(minutes=1):
                    raise OtpRequestToSoon()
                if item.created_at > timezone.now() - timedelta(minutes=10):
                    count_10_min += 1
                if item.created_at > timezone.now() - timedelta(hours=24):
                    count_24_hours += 1
            if count_10_min > 3:
                print(count_10_min)
                raise OtpShortTermLimitExceeded()
            if count_24_hours > 20:
                raise OtpDailyLimitExceeded()
            otp.active = False
            otp.save()
            new_otp = Otp.objects.create(identifier=otp.identifier, code=randint(1000, 9999))
            return new_otp
        except Otp.DoesNotExist:
            raise InvalidOtpError()
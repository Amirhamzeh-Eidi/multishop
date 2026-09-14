from .models import Otp
from  django.utils import timezone
from datetime import timedelta
import secrets
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
        otp.active = False
        otp.save(update_fields=["active"])
        return otp

    def resend_otp(token):
        try:
            otp = Otp.objects.get(token=token)
            otps = Otp.objects.filter(identifier=otp.identifier)
            count_1_min = Otp.objects.filter(identifier=otp.identifier, created_at__gte=timezone.now() - timedelta(minutes=1))
            count_10_min = Otp.objects.filter(identifier=otp.identifier, created_at__gte=timezone.now() - timedelta(minutes=10))
            count_24_hours = Otp.objects.filter(identifier=otp.identifier, created_at__gte=timezone.now() - timedelta(hours=24))
            if count_1_min.exists():
                raise OtpRequestToSoon()
            if count_10_min.count() >= 3:
                raise OtpShortTermLimitExceeded()
            if count_24_hours.count() >= 20:
                raise OtpDailyLimitExceeded()
            otp.active = False
            otp.save()
            new_otp = Otp.objects.create(identifier=otp.identifier, code=str(secrets.randbelow(9000)+1000))
            return new_otp
        except Otp.DoesNotExist:
            raise InvalidOtpError()
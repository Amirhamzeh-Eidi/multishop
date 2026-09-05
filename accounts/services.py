from .models import Otp
from  django.utils import timezone
class ExpiredOtpError(Exception):
    pass
class ToManyAttemptsError(Exception):
    pass
class WrongOtpError(Exception):
    pass
class InvalidOtpError(Exception):
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

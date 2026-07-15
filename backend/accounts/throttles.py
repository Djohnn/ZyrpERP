from rest_framework.throttling import AnonRateThrottle


class RegistrationThrottle(AnonRateThrottle):
    scope = 'auth_register'


class LoginThrottle(AnonRateThrottle):
    scope = 'auth_login'


class PasswordRecoveryThrottle(AnonRateThrottle):
    scope = 'auth_password'


class MFAThrottle(AnonRateThrottle):
    scope = 'auth_mfa'

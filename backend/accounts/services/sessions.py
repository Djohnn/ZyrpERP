from django.contrib.sessions.models import Session
from django.utils import timezone


def revoke_user_sessions(user_id):
    for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator():
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user_id):
            session.delete()

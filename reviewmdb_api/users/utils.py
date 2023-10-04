from django.core.mail import send_mail


def send_confirmation_code(email, confirmation_code):
    """Oтправляет на почту пользователя код подтверждения."""
    send_mail(
        'Подтверждение регистрации.',
        f'Направляем confirmation_code: {confirmation_code}',
        'admin@yamdb.com',
        [email],
        fail_silently=False,
    )

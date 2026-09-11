from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings


templates = Jinja2Templates(directory="static/templates/email")


async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:
    message = EmailMessage()
    message['From'] = settings.MAIL_HOST_USER
    message['To'] = to_email
    message['Subject'] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype='html')


    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD.get_secret_value(),
        use_tls=True,      
        start_tls=False, 
    )




async def send_password_reset_email(
    to_email: str,
    username: str,
    token: str
) -> None:

    reset_url = f'{settings.FRONTEND_URL}/security/reset-password?token={token}'

    template = templates.env.get_template('password_reset.html')
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""
                        Здравствуйте, {username}!

    Вы запросили сброс и смену пароля. Перейдите по ссылке ниже, чтобы задать новый пароль:

    {reset_url}

    ❗️ Ссылка активна 1 час.

    Если вы не запрашивали сброс пароля, обратитесь в службу поддержки для разъяснения ситуации:
    zub_daem_pomozhem@ne_vrem.ru
 
    
    С уважением,
        команда roma_lbj
    """

    await send_email(
        to_email=to_email,
        subject='Сброс пароля на FastApi by roma_lbj',
        plain_text=plain_text,
        html_content=html_content
    )
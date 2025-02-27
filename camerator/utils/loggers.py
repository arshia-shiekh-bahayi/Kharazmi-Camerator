import logging

from django.conf import settings
from django.core.mail import send_mail

general_logger = logging.getLogger("general_logger")
console_file_logger = logging.getLogger("console_file_logger")


class EmailLogHandler(logging.Handler):
    def emit(self, record):
        subject = f"Exception: {record.levelname}"
        body = self.format(record)
        send_mail(
            subject,
            body,
            "log@camerator.ir",
            settings.LOG_EMAIL_RECEIVERS,
            fail_silently=False,
        )


log_file = settings.BASE_DIR / "logs/general_logger.log"
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# File Log Handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

# Console Log Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_format)

# Email Log Handler
email_handler = EmailLogHandler()
email_handler.setLevel(logging.WARNING)
email_handler.setFormatter(log_format)


general_logger.addHandler(console_handler)
general_logger.addHandler(file_handler)
general_logger.addHandler(email_handler)

console_file_logger.addHandler(console_handler)
console_file_logger.addHandler(file_handler)

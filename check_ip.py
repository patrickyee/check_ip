import smtplib
import subprocess


EXPECTED_IP = '123.123.123.123'
COMMAND = 'host myip.opendns.com resolver1.opendns.com'.split()
LOGIN_USER = 'my_user_name@gmail.com'
LOGIN_PASSWORD = 'fill_me_in'
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
TO_ADDRESS = 'my_user_name@gmail.com'
SUBJECT = 'my subject'


def send_email(subject, body):
    s = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    s.starttls()
    s.ehlo()
    s.login(LOGIN_USER, LOGIN_PASSWORD)
    s.sendmail(LOGIN_USER, TO_ADDRESS, f'Subject: {subject}\n{body}')


def run():
    shell_output = subprocess.run(COMMAND, capture_output=True)
    if shell_output.returncode != 0:
        send_email(SUBJECT + ' Failed', shell_output.stderr.decode('UTF-8'))
        return

    lines = [line.strip() for line in shell_output.stdout.decode('UTF-8').split('\n') if line.strip()]
    current_ip = lines[-1].split(' ')[-1]

    if EXPECTED_IP != current_ip:
        send_email(SUBJECT, f'IP changed from {EXPECTED_IP} to {current_ip}')


if __name__ == '__main__':
    run()

import argparse
import smtplib
import subprocess
import os
from dotenv import load_dotenv


# load environment variables
load_dotenv()


# command to find current IP
COMMAND = 'host myip.opendns.com resolver1.opendns.com'.split(' ')


class CheckIP:
    def __init__(self, args, password):
        self.args = args
        self.password = password
        self.run()

    def get_mail_port(self, host):
        """Gets a mail port from a SMTP mail host server (small list of options right now, might add more)."""

        if host in {'smtp.gmail.com', 'smtp-mail.outlook.com'}:
            return 587
        elif host == 'smtp.mail.yahoo.com':
            return 465
        return 25

    def send_email(self, *, subject=None, body):
        """Sends an encrypted email through smtplib."""

        if not subject:
            # set default subject
            subject = self.args.email_subject
        
        # initialize object
        s = smtplib.SMTP(self.args.smtp_host, self.get_mail_port(self.args.smtp_host))

        # encrypt connection and login
        s.connect()
        s.starttls()
        s.ehlo()
        s.login(self.args.email, self.password)

        # send actual email
        s.sendmail(
            self.args.email,
            self.args.email_recipient,
            f'Subject: {subject}\n{body}'
        )

    def run(self):
        """Checks if expected and current IP addresses are the same."""
        
        # run command to find current IP address
        shell_output = subprocess.run(COMMAND, capture_output=True)

        # check if operation went successfully
        if shell_output.returncode != 0:
            # send a failure email
            self.send_email(subject=self.args.email_subject + ' Failed', body=shell_output.stderr.decode('UTF-8'))
            return
        
        # decode shell output to Unicode, split by newline, and strip all applicable lines of the output
        lines = [line.strip() for line in shell_output.stdout.decode('UTF-8').split('\n') if line.strip()]

        # find current IP address
        current_ip = lines[-1].split(' ')[-1]
        
        # check if expected and current IP addresses are the same
        if self.args.ip != current_ip:
            # send an email citing the change
            self.send_email(body=f'IP changed from {self.args.ip} to {current_ip}')

        # even if the IP did not change, send an email if the '--report' option is enabled
        elif self.args.report_mode:
            self.send_email(body=f'IP remained at {current_ip}')



if __name__ == '__main__':
    # get password from .env
    password = os.environ['PASSWORD']

    # initialize argument parser
    parser = argparse.ArgumentParser(description='Detect IP change')

    # add an argument 'report'
    # - with the target attribute 'report_mode'
    # - storing the appearance of the arg (boolean)
    parser.add_argument('--report', dest='report_mode', action='store_true', help='Send report email')

    # add an argument 'email'
    # - storing the email address of the sender (string)
    parser.add_argument('email', action='store', help='Sender\'s email address')

    # add an argument 'ip'
    # - storing the expected IP address (string)
    parser.add_argument('ip', action='store', help='Expected IP address')

    # add an argument 'subject'
    # - with the target attribute 'email_subject'
    # - storing the subject of the report email
    parser.add_argument('--subject', dest='email_subject', action='store', default='IP Check Result', help='Subject of report email')

    # add an argument 'recipient'
    # - with the target attribute 'email_recipient'
    # - storing the recipient of the report email
    parser.add_argument('--recipient', dest='email_recipient', action='store', help='Recipient of report email')

    # add an argument 'host'
    # - with the target attribute 'smtp_host'
    # - storing the SMTP host
    parser.add_argument('--host', '-host', dest='smtp_host', action='store', help='SMTP host')

    # parse sys.argv() (system arguments)
    args = parser.parse_args()

    # TODO: add comment concerning actions of run()
    CheckIP(args=args, password=password)

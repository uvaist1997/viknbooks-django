import threading
from django.core.mail import EmailMessage


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content,sender, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.recipient_list,self.sender)
        msg.content_subtype = 'html'
        msg.send()


def send_html_mail(subject, html_content, sender,recipient_list):
    EmailThread(subject, html_content,sender, recipient_list).start()
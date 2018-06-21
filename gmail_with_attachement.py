

import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
import  mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from apiclient import errors, discovery
import pandas as pd
from datetime import date, timedelta
import pyodbc





def get_credentials(): # Gets valid user credentials from disk.
    SCOPES = 'https://www.googleapis.com/auth/gmail.send'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Gmail API Python Send Email'
    credential_dir = '***credential_dir***'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def SendMessage(sender, to, cc, subject, message_text, file):
    credentials = get_credentials()
    #print (credentials)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message1 = CreateMessage(sender, to, cc,subject, message_text, file)
    SendMessageInternal(service, "me", message1)

def SendMessageInternal(service, user_id, message):
    """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        # print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % str(error)[0:200])

def CreateMessage(
    sender, to, cc, subject, message_text, file):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['cc'] =  cc
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, 'html')
    message.attach(msg)

    with open(file, 'rb') as fp:
        msg = MIMEBase('application', "octet-stream")
        msg.set_payload(fp.read())
        encoders.encode_base64(msg)

    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(str(message).encode('UTF-8')).decode('ascii')}
    # return {'raw': base64.urlsafe_b64encode(message.as_string())}





def main():
    # 'marc-olivier.dupont-vezina@brp.com'

    sender = "***EMAIL***"
    to = '***EMAIL***'
    cc = '***EMAIL***'
    subject = "TITLE"
    message_text = """
                    <span style="display:inline-block; width: 600;">
                    Hi,<br>
                    Here is this week's report.

                    If you find errors,have any questions or concerns on this report please contact:<br>
                    <li><strong> ***NAME***</strong>: ***EMAIL***</li>
                    </span>
                    """
    file_location = '***FILE***'

    SendMessage(sender, to, cc,subject, message_text, file_location)


if __name__ == '__main__':
    main()
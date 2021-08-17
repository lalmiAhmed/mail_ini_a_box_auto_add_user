from __future__ import print_function
import imaplib
import email
import time
import mailinabox_api
from mailinabox_api.rest import ApiException
from pprint import pprint
import re

def auto_add_users():
    host = 'imap.gmail.com'
    username = '' #your email
    password = '' #your passowrd

    def get_inbox():
        mail = imaplib.IMAP4_SSL(host)
        mail.login(username, password)
        mail.select("inbox")
        _, search_data = mail.search(None, 'ALL')
        my_messages = []
        # print ( "you have", len(search_data[0].split()),"messages in your account")
        for num in search_data[0].split():
            email_data = {}
            _, data = mail.fetch(num, '(RFC822)')
            # print(data[0])
            _, b = data[0]
            email_message = email.message_from_bytes(b)
            for header in ['subject', 'to', 'from', 'date']:
                # print("{}: {}".format(header, email_message[header]))
                email_data[header] = email_message[header]
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    email_data['body'] = body.decode()
                elif part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True)
                    email_data['html_body'] = html_body.decode()
            my_messages.append(email_data['body'].split('\r\n')) # I assumed that the first line should contains only the username and second line will contians only passws
        return my_messages

    #fetch function: checks if the length of the inbox_list changed from the last call if yes then it will append the new ones to fetched_list and return it, if the lenght dosen't changed the return an empty list
    def fetch_emails(last_call_leng):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$' #regex for valid email address
        new_mails = []
        last_call_leng = len(new_mails)
        all_messages = get_inbox()
        num_of_new = len(all_messages)-last_call_leng
        if num_of_new != 0:
            for n_msg in range(len(all_messages)-1,len(all_messages)-1-num_of_new,-1):
                h_list = []
                if bool(re.search(regex, all_messages[n_msg][0])):
                    for e in range(2):
                        if len(all_messages[n_msg])>=2 and all_messages[n_msg][e].strip() != "":
                            h_list.append(all_messages[n_msg][e].strip())
                    if h_list != []:
                        new_mails.append(h_list)

        return new_mails

    # make loop that fetch new messages from the top each X seconds
    delay = 60*10 # in seconds (each 10 minutes)
    last_call_leng = 0

    # Defining the host is optional and defaults to https://box.example.com/admin
    configuration = mailinabox_api.Configuration(
        host = "https://box.example.com/admin"
    )
    # The client must configure the authentication and authorization parameters
    # in accordance with the API server security policy.
    # Configure HTTP basic authorization: basicAuth
    configuration = mailinabox_api.Configuration(
        username = 'YOUR_USERNAME',
        password = 'YOUR_PASSWORD'
    )

    while True:
        # fetch 
        new_mails = fetch_emails(last_call_leng)
        print("number of new (valid) emails : ",len(new_mails)) # we can check that by email valid
        # print(new_mails)
        #update last call leng
        last_call_leng = len(new_mails)

        #adding users
        for user_info in new_mails:
            # Enter a context with an instance of the API client
            with mailinabox_api.ApiClient(configuration) as api_client:
                # Create an instance of the API class
                api_instance = mailinabox_api.MailApi(api_client)
                email = user_info[0] # str | Email format.
            password = user_info[1] # str | 
            privileges = mailinabox_api.MailUserPrivilege() # MailUserPrivilege | 
            try:
                # Add mail user
                api_response = api_instance.add_mail_user(email, password, privileges)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling MailApi->add_mail_user: %s\n" % e)

        print("getting new mails ...\n\n")
        time.sleep(delay)

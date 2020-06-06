import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

def load_mailing_list():
	file = open("{}/mailing_list.txt".format(sys.path[0]), 'r')
	mailing_list = file.readlines()
	file.close()
	return mailing_list


def send_email(subject, message, my_address, password):
	# login to email
    s = smtplib.SMTP(host='smtp.office365.com', port=587)
    s.ehlo()
    s.starttls()
    # s.ehlo()
    s.login(my_address, password)

    msg = MIMEMultipart()  # create a message

    mailing_list = load_mailing_list()

    for email in mailing_list:
	    # setup the parameters of the message
	    msg['From']=MY_ADDRESS
	    msg['To']=email
	    msg['Subject']=subject
	    
	    # add in the message body
	    msg.attach(MIMEText(message, 'plain'))
	    
	    # send the message via the server set up earlier.
	    s.send_message(msg)
	    del msg
        
    # Terminate the SMTP session and close the connection
    s.quit()

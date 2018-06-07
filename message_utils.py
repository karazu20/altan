# -*- coding: utf-8 -*-
import datetime
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import paramiko
from slackclient import SlackClient
import os
import time




#Params gmail server and email accounts
mail_server = 'smtp.gmail.com:587'
from_addr = 'Altan monitor.altanredes@gmail.com'
to_addr = [ 'rodolfo.daniel.hernandez.torres@everis.com',
			'carlos.alberto.lopez.ramirez@everis.com', 
			'moises.francisco.almanza.aquino@everis.com' ]
	
# Credentials email
username = 'monitor.altanredes@gmail.com'
password = 'MONITOREOaltan123'

#paramiko.util.log_to_file("paramiko.log")
#source= '/home/carlos/Documentos/altan-master/escribe.txt'
#destination ='/data/disk0/input/apigee/escribe.txt'

#Params server sftp
sftp_server='34.237.230.77'
sftp_port = 2222
sftp_user='apigee'
path_cert = 'misc/altan-apigee-edge'



#Params slack
os.environ["SLACK_BOT_TOKEN"]="xoxp-376147001620-377262535558-377674263634-d82612553ba126ddac30cc0e06ea12e0"
slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
channel = "#monitor_altanredes"

#Url para generar token https://api.slack.com/custom-integrations/legacy-tokens


def sendSlack(message):
	print message
	sc.api_call(
	  "chat.postMessage",
	  channel=channel,
	  text=message
	)									
	print "Slack ok"


#sudo sftp -i altan-apigee-edge -P 2222 apigee@34.237.230.77
def sendFile(source, destination):
	try:
	    client = paramiko.SSHClient()
	    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    k = paramiko.RSAKey.from_private_key_file(path_cert)
	    client.load_system_host_keys()
	    client.connect(sftp_server, port=sftp_port, username=sftp_user, pkey = k)

	    sftp = client.open_sftp()
	    sftp.put(source, destination)

	finally:
	    client.close()



def sendMail (errores, hours):	
	themsg = MIMEMultipart('alternative')
	themsg['Subject'] = 'Errores Apigee'
	themsg['To'] = ", ".join(to_addr)
	themsg['From'] = from_addr
	html = '''
		<html>
			<head></head>
			<body>
				
				<br>
				<h3>Errores detectados entre %s</h3>
				<br>
				<p>
					Se detectaron los siguientes errores 
				</p>

				<p>
					Detalle de errores:  
					
				</p>
				<br>
					<p>
						%s
					</p>
				<br>
				<p>
					Gracias!!.
				</p>
				
			</body>
		</html>
	''' % (hours, errores)

	part2 = MIMEText(html, 'html', 'utf-8')
	themsg.attach(part2)
	server = smtplib.SMTP(mail_server)
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(from_addr, to_addr, str(themsg))
	server.quit()

	print 'Email ok'



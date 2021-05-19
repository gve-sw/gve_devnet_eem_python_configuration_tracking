import os
from cli import cli
import time
import difflib
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import mimetypes


def save_config():
  output = cli('show run')
  timestr = time.strftime("%Y%m%d-%H%M%S")
  filename = "/bootflash/guest-share/" + timestr + "_shrun"

  f = open(filename,"w")
  f.write(output)
  f.close

  f = open('/bootflash/guest-share/current_config_name','w')
  f.write(filename)
  f.close

  return filename

def compare_configs(cfg1,cfg2):

  d = difflib.unified_diff(cfg1, cfg2)

  diffstr = ""

  for line in d:
    if line.find('Current configuration') == -1:
      if line.find('Last configuration change') == -1:
        if (line.find("+++")==-1) and (line.find("---")==-1):
          if (line.find("-!")==-1) and (line.find('+!')==-1):
            if line.startswith('+'):
              diffstr = diffstr + "\n" + line
            elif line.startswith('-'):
              diffstr = diffstr + "\n" + line
  return diffstr

def send_email_notifciation(gmail_username:str, gmail_password:str ,sender: str, receivers: list, message=None, device_hostname="Insert-Hostname-Here"):
  
  # Create the container (outer) email message.
  msg = EmailMessage()
  # me == the sender's email address
  # family = the list of all recipients' email addresses
  msg['From'] = sender
  msg['To'] = ', '.join(receivers)
  msg['Subject'] = "Configuration Change Alert!"

  msg.set_content(message)

  # now create a Content-ID for the image
  # if `domain` argument isn't provided, it will 
  # use your computer's name
  image_cid = make_msgid(domain="example.com")

  #sert an alternative html body
  msg.add_alternative("""\
    <html>
      <body>
        <div style= "width: 90%; height: 120%;" >
          <img src ="cid:{image_cid}" style=" width: 85%; height: 25%; border: 2px ; outline-style: solid; outline-color: #00bceb;">
          <p style="width: 85%; font-size: 24px; border: 2px ; outline-style: solid; outline-color: #00bceb; background-color: white;">
            The network device - <strong style="font-style: italic; font-size: 24px">{device_hostname}</strong> - has experienced a configuration change!
          </p>
          <div style= "width: 85%; height: auto; border: 2px ; outline-style: solid; outline-color: #00bceb;">

            <p style="background-color: white;">
            <strong style= "font-size: 24px;"> Configuration Difference Below: </strong>

            </p>

           
            <p style="background-color: lightgrey;">
              <code style="font-size: 16px;">
                {message}
              </code>
            </p>
          </div>
      </div>
      </body>
    </html>
    """.format(image_cid=image_cid[1:-1], device_hostname=device_hostname, message=message), subtype='html')
  # image_cid looks like <long.random.number@xyz.com>
  # to use it as the img src, we don't need `<` or `>`
  # so we use [1:-1] to strip them off


  # Open the files in binary mode.  Let the MIMEImage class automatically
  # guess the specific image type.
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ConfigChangeAlert.png"), 'rb') as img:
    maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
    msg.get_payload()[1].add_related(img.read(),maintype=maintype, subtype=subtype,cid=image_cid)

  # Send the email via our own SMTP server.
  mailServer = smtplib.SMTP('smtp.gmail.com', 587)
  mailServer.ehlo()
  mailServer.starttls()
  mailServer.ehlo()
  mailServer.login(gmail_username, gmail_password)
  mailServer.sendmail(sender, receivers, msg.as_string())
  mailServer.close()

if __name__ == '__main__':

  old_cfg_fn = "/bootflash/guest-share/base_config"
  new_cfg_fn = save_config()

  f = open(old_cfg_fn)
  old_cfg = f.readlines()
  f.close

  f = open(new_cfg_fn)
  new_cfg = f.readlines()
  f.close

  diff =  compare_configs(old_cfg,new_cfg)
  f = open("/bootflash/guest-share/diff","w")
  f.write(diff)
  f.close

  #AN EXAMPLE OF A DIFF CREATED BY THE PROGRAM CAN BE SEEN BELOW.
#   diff = """\

# +Building configuration...\n

# +logging console notifications\n

# +archive\n

# + log config\n

# +  logging enable\n

# +event manager applet email_config_change\n

# + event syslog pattern "SYS-5-CONFIG_I"\n

# + action 0 cli command "enable"\n

# + action 1 cli command "guestshell run python3 /bootflash/guest-share/email_cfg.py"\n

#   """

  send_email_notifciation("gmailusername", "gmailpassword", "senders_email@example.com", ["receivers_email@example.com"], diff.replace("\n", "<br>") )

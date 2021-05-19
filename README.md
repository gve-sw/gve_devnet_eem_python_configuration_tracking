# GVE_DevNet_EEM_Python_Configuration_Tracking
This document will showcase examples of how to trigger a python script based off of an event on an IOS device. Specifically, this document speaks to the use-case: “We want to track configuration changes made by users, and send an email when a change is made.” This document will showcase examples of python code and EEM configurations on IOS devices.

## Contacts
* Charles Llewellyn (chllewel@cisco.com)

## Solution Components
* IOS
*  EEM
*  WLC
*  Python
*  Linux


## Getting Started:



To get started, we first want to check if guestshell is already installed as an app on our device:


Check if the IOX Services are enabled and running.




If the guestshell app is not found when using the command “sh app-hosting list” - We will need to configure guest shell using the commands below.
![/IMAGES/guestshell-1.png](/IMAGES/guestshell-1.png)
![/IMAGES/guestshell-2.png](/IMAGES/guestshell-2.png)

Lastly, enable and run guestshell:
![/IMAGES/guestshell-3.png](/IMAGES/guestshell-3.png)



## Writing The Python Script:

Once guestshell is enabled, we can write our python script into a file in the guestshell. 

The script in this repo sends an email to a user when a configuratin change occurs. It can be found [here](/cfg.py)

An Example of the email can be seen below:
![/IMAGES/Email_Example_Screenshot.png](/IMAGES/Email_Example_Screenshot.png)


### For this example we will write the below python script to the location: /bootflash/guest-share/cfg.py

![/IMAGES/UserTracking1.png](/IMAGES/UserTracking1.png)


When run, this script get the current running configuration on the IOS device, and compare it to the old configuration on the device to check for differences. The differences will then be written to a file and emailed to a specified email address.

Now the only thing left to do is create an EEM applet to run this script on triggered events!

## EEM Event Syslog Patterns:


Before we write our EEM applet, lets first look at what events we will be using to trigger our script.

For this example we will be triggering our event when a specific type of syslog message appears on our device. 

### Here are some different syslog patterns that we can use, and the reason we would use them:

* “SYS-5-CONFIG_I” - This message will send after a user has exited configuration mode on the terminal - after making a change to the current configuration.

* “SYS-5-CONFIG_P” - This message will send after a user has made configuration changes to the device using the GUI. (Note: This message does not get sent after all config changes via the GUI).

* “SYS-6-PRIVCFG_ENCRYPT_SUCCESS” - This message will send after a user has saved written the running configuration to the startup configuration. This message will send for changes that were made from the terminal and the GUI. 

* “SEC_LOGIN-5-LOGIN_SUCCESS” -  This message will send after a user has logged into the device. This triggers on both GUI and terminal vty logins. 

* “SYS-6-LOGOUT” - This message will send after a user has logged out of the device.




Below is an example of some of these patterns being used for an EEM applet. This applet example shows how we can trigger our python script using syslog patterns. 
![/IMAGES/EEM_Example.png](/IMAGES/EEM_Example.png)

## High Level Design:


For the last section of this guide, we will walk through the steps of creating an EEM applet and then a quick look at the high level design of triggering a python script via system events using the EEM applet.

First we must create our EEM applet:



Once the applet has been created, the applet actions will trigger whenever the event syslog pattern is created.

 In this example, the applet runs the command “enable” and then runs the python script using the command  “guestshell run python3 /path/to/file.py”.

Below is a visualization of this process.

![/IMAGES/EEM_process.png](/IMAGES/EEM_process.png)


# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.

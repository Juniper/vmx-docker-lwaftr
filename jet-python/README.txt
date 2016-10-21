=========================================
Juniper JET API client package

Junos-Jet-API package enables users to remotely program and monitor JUNOS devices. This package con
tains the following folders:
    1. doc - Extensive documentation is provided with the distribution. All the service definitions
 are present in the html and pdf files in this folder.
    2. lib - This folder contains the package implementation code.
    3. examples - This folder contains examples for all the services available in this client packa
ge version.

Users need to enable the following configurations on JUNOS box (JET servers) before using the JET c
lient package.
    1. Enable Netconf by executing the following command in the configuration mode:
        #set system services netconf ssh
    2. Enable JET services by executing the following command in the configuration mode:
        #set system services jet [traceoptions flag all]
    3. If localhost is not configured please configure it using the following command:
        #set interfaces lo0 unit 0 family inet address 127.0.0.1/24
    4. Apply all the above configurations by executing 'commit' command.

Steps to use the Client Package:
    1. Install the package using 'pip install junos-jet-api.tgz'.
    2. Open the user's choice of Python editor.
    3. To verify if the installation worked properly:
           - Invoke the Python interpreter.
           - Execute 'from jnpr.jet import JetHandler'
           - Successful installation will not throw any error.
    4. Start writing your JET application by referring to the examples folder for sample applicatio
ns and doc folder for API usage.

If pip is not available on the client machines, please follow these steps to install package:
    1. Download and install thrift>= 0.9.2 version.
    2. Download and install paho-mqtt>=1.0 version.
    3. Untar the client package and change to junos-jet-api directory
    4. Execute 'python setup.py install'. In most of the cases, you need to be the root user for this 
       command to work properly, so you can try 'sudo python setup.py install' command instead.
    5. Open the user's choice of Python editor.
    6. To verify if the installation worked properly:
           - Invoke the Python interpreter.
           - Execute 'from jnpr.jet import JetHandler'
           - Successful installation will not throw any error.
    7. Start writing your JET application by referring to the examples folder for sample applicatio
ns and doc folder for API usage.

Please check the file required.txt for the dependent packages.

For Off-box deployment of the apps, no additional steps are needed. Users can just execute their apps as standalone processes.

For On-box deployment of the apps, users do not need to include the client libraries in their package 
as the client package libraries is already available when JET service is enabled on the JUNOS box. 
Please follow these instructions for On-box deployments of the app:

If the app doesn't have dependencies on C/C++ code and app need not be signed, the recommendation is to use Python distutils tools for creating the package. Otherwise use JET VM image for packaging and signing the app.
	
Steps for packaging pure python and unsigned apps: 
    1. Write setup.py script
    2. Run 'python setup.py sdist formats=gztar'

The <app>.tar.gz file gets created; this file should be ftp'd to JUNOS box, and run request system software add <app>.tar.gz to install the app. After installation is complete, follow below steps to run the app.

The app should be configured under the below mentioned hierarchy and commit. 
If app expects any arguments, it should also be configured. And if the app is a long running daemon, the `daemonize` config should be enabled.
    # set system services jet application file <app>.py
    # set system services jet application file <app>.py arguments "list of arguments" ---> if any.
    # set system services jet application file <app>.py daemonize   ---> set if app is a long running daemon.

If the app is not signed, enable below configuration and commit.
    # set system scripts language python

Run these operational commands to start or stop the app.
    cli> request extension-service start <appname>
    cli> request extension-service stop <appname>

To check status of the running apps, use below mentioned operational commands.
    cli> show extension-service status <app-name>
    cli> show extension-service status all 

    The details displayed for each app would be: 
    -	Name of the App
    -	Process-Id of the App.
    -   Arguments list if any. 
    - 	Memory utilization.
    -	CPU utilization. 


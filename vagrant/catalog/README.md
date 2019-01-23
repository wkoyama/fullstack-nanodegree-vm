# APIs
### This is the code Repo for ud388 - Designing RESTful APIs

This code base was meant to supplement the Udacity course for designing RESTful APIs.  Within each directory you will find sample and solution code to the exercises in this course.  Some of this code will require some modification from the user before it is executable on your machine.

## API Keys for third party providers
This course uses the Google Maps and Foursquare APIs. You will need to create developer accounts and private keys in order to properly use code snippets that rely on these APIs.

## Python Libraries
The code in this repository assumes the following python libraries are installed:
* Flask
* SQLAlchemy
* httplib
* requests
* oauth2client
* redis
* passlib
* itsdangerous
* flask-httpauth

## Installing Redis
      wget http://download.redis.io/redis-stable.tar.gz
      tar xvzf redis-stable.tar.gz
      cd redis-stable
      make install

Visão geral do projeto
Você desenvolverá um aplicativo que fornece uma lista de itens em uma variedade de categorias, bem como um sistema de registro e autenticação de usuários. Usuários registrados terão a capacidade de postar, editar e excluir seus próprios itens.

Installing the Vagrant VM
Note: If you already have a vagrant machine installed from previous Udacity courses skip to the 'Fetch the Source Code and VM Configuration' section

In this course, you'll use a virtual machine (VM) to run a web server and a web app that uses it. The VM is a Linux system that runs on top of your own machine. You can share files easily between your computer and the VM.

We're using the Vagrant software to configure and manage the VM. Here are the tools you'll need to install to get it running:

Git
If you don't already have Git installed, download Git from git-scm.com. Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash). (On Mac or Linux systems you can use the regular terminal program.)

You will need Git to install the configuration for the VM. If you'd like to learn more about Git, take a look at our course about Git and Github.

VirtualBox
VirtualBox is the software that actually runs the VM. You can download it from virtualbox.org, here. Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

Ubuntu 14.04 Note: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.

Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. You can download it from vagrantup.com. Install the version for your operating system.

Windows Note: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

Fetch the Source Code and VM Configuration
Windows: Use the Git Bash program (installed with Git) to get a Unix-style terminal.

Other systems: Use your favorite terminal program.

Fork the starter repo
Log into your personal Github account, and fork the oauth repo so that you have a personal repo you can push to for backup. Later, you'll be able to use this repo for submitting your projects for review as well.

Clone the remote to your local machine
From the terminal, run the following command (be sure to replace <username> with your GitHub username): git clone http://github.com/<username>/OAuth2.0 oauth

This will give you a directory named oauth that is a clone of your remote OAuth2.0 repository, complete with the source code for the flask application, a vagrantfile, and a pg_config.sh file for installing all of the necessary tools.

Run the virtual machine!
Using the terminal, change directory to oauth using the commandcd oauth, then type vagrant up to launch your virtual machine.

Running the Restaurant Menu App
Once it is up and running, type vagrant ssh. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type exit at the shell prompt. To turn the virtual machine off (without deleting anything), type vagrant halt. If you do this, you'll need to run vagrant up again before you can log into it.

Now that you have Vagrant up and running type vagrant ssh to log into your VM. Change directory to the /vagrant directory by typing cd /vagrant. This will take you to the shared folder between your virtual machine and host machine.

Type ls to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Now type python database_setup.py to initialize the database.

Type python lotsofmenus.py to populate the database with restaurants and menu items. (Optional)

Type python project.py to run the Flask web server. In your browser visit http://localhost:5000 to view the restaurant menu app. You should be able to view, add, edit, and delete menu items and restaurants.
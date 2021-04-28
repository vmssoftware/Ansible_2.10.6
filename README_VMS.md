How to start using Ansible with OpenVMS
=======================================
On OpenVMS:
----------
- Install Python for OpenVMS (version 3.8-2 or later). Refer to https://vmssoftware.com/products/python/ for the installer and the Release notes.
- Ensure that the symbol "python" is defined in your login.com
- Ensure that "set process/parse_style=extended in your login.com

On Linux:
--------
- Ensure that Python is installed on your Linux system or install it from the official site (https://www.python.org/). Also, install python-paramiko, python-crypto, python-yaml, python-jinja2 packages.
- Download Ansible to the Linux system: git clone https://github.com/vmssoftware/Ansible_2.10.6.git
- setup Ansible by executing the following command from the top-level Ansible source directory: sudo python3 setup.py install
- set the environment variable ansible_shell: ansible_shell_type=dcl (edited)

Try to run the 'ping' command to ensure that Ansible is successfully installed and configured:
- simple config: edit hosts file (/etc/ansible/hosts)
if you have an ssh key
[host_name]
IP ansible_shell_type=dcl ansible_ssh_user=USER ansible_ssh_private_key_file=PATH
or if you have password
[host_name]
IP ansible_shell_type=dcl ansible_ssh_user=USER ansible_ssh_pass=PASSWORD
- now test the connection with the command: ansible host_name -m ping
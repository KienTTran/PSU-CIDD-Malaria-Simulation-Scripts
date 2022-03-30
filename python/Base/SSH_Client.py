## Handles the connection to the cluster
import paramiko     #Provides SSH functionality
import os           #Used to setup the Paramiko log file
import logging      #Used to setup the Paramiko log file
import socket       #This method requires that we create our own socket

## From https://stackoverflow.com/questions/53761170/ssh-with-2fa-in-python-using-paramiko
class SSHClient(paramiko.SSHClient):
    duo_auth = True

    def handler(self, title, instructions, prompt_list):
        answers = []
        for prompt_, _ in prompt_list:
            prompt = prompt_.strip().lower()
            if prompt.startswith('password'):
                answers.append(self.password)
            elif prompt.startswith('verification'):
                answers.append(self.totp)
            elif prompt.startswith('duo two-factor login for'):
                answers.append(self.totp)
            else:
                raise ValueError('Unknown prompt: {}'.format(prompt_))
        return answers

    def auth_interactive(self, username, handler):
        if not self.totp:
            raise ValueError('Need a verification code for 2fa.')
        self._transport.auth_interactive(username, handler)

    def _auth(self, username, password, pkey, *args):
        self.password = password
        saved_exception = None
        two_factor = False
        allowed_types = set()
        two_factor_types = {'keyboard-interactive', 'password', 'publickey'}

        if self.duo_auth or two_factor:
            logging.info('Trying 2fa interactive auth')
            return self.auth_interactive(username, self.handler)

        if password is not None:
            logging.info('Trying password authentication')
            try:
                self._transport.auth_password(username, password)
                return
            except paramiko.SSHException as e:
                saved_exception = e
                allowed_types = set(getattr(e, 'allowed_types', []))
                two_factor = allowed_types & two_factor_types

        assert saved_exception is not None
        raise saved_exception
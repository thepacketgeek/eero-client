#!/usr/bin/env python
from argparse import ArgumentParser
import os
import json
import eero
import six


class CookieStore(eero.SessionStorage):
    def __init__(self):
        self.cookie_file = None
        self.__cookie = None

    def from_file(cookie_file):
        store = CookieStore()
        store.cookie_file = os.path.abspath(cookie_file)

        try:
            with open(store.cookie_file, 'r') as f:
                store.__cookie = f.read()
        except IOError:
            pass

        return store
            

    def from_token(user_token):
        store = CookieStore()
        store.__cookie = user_token
        return store

    @property
    def cookie(self):
        return self.__cookie

    @cookie.setter
    def cookie(self, cookie):
        self.__cookie = cookie
        if self.cookie_file:
            with open(self.cookie_file, 'w+') as f:
                f.write(self.__cookie)





def print_json(data):
    print(json.dumps(data, indent=4))

COMMANDS = [
    'devices',
    'details',
    'info',
    'eeros',
    'reboot',
    'speedtest',
    'clients',
    'diagnostics',
    'resources',
    'support',
    'forwards',
    'reservations',
    'settings',
]

if __name__ == '__main__':
    if token := os.getenv("EERO_TOKEN"):
        session = CookieStore.from_token(token)
    else:
        session = CookieStore.from_file('session.cookie')
    eero = eero.Eero(session)

    if eero.needs_login():
        parser = ArgumentParser()
        parser.add_argument("-l", help="your eero login (email address or phone number)")
        args = parser.parse_args()
        if args.l:
            phone_number = args.l
        else:
            phone_number = six.moves.input('your eero login (email address or phone number): ')
        user_token = eero.login(phone_number)
        verification_code = six.moves.input('verification key from email or SMS: ')
        eero.login_verify(verification_code, user_token)
        print('Login successful. Rerun this command to get some output')
    else:
        account = eero.account()

        parser = ArgumentParser()
        parser.add_argument("command",
                            choices=COMMANDS,
                            help="info to print")
        parser.add_argument("--eero", type=int, help="eero to reboot")
        args = parser.parse_args()

        for network in account['networks']['data']:
            if args.command == 'info':
                print_json(network)
            elif args.command == 'details':
                network_details = eero.networks(network['url'])
                print_json(network_details)
            elif args.command == 'resources':
                resources = eero.resources(network['url'])
                print_json(resources)
            else:
                output = eero.get_resource(args.command, network['url'])
                print_json(output)


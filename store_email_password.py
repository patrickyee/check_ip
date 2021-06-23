import getpass


if __name__ == '__main__':
    password = getpass.getpass('Enter your email password: ')
    with open('.env', 'w+') as f:
        f.write(f'export PASSWORD={password}')

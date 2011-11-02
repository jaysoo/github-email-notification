'''
Settings for the service
'''
settings = {
    # The hostname and port to listen on
    'host': 'localhost',
    'port': 8000,

    # Whitelisted IP that are allowed to access this service
    'addr_whitelist': [
        '127.0.0.1',

        # GitHub's IP address
        '207.97.227.253',
    ],

    # Email sender
    'email_from': 'User <user@example.com>',

    # List of addresses to send to
    'email_to': [
        'user@example.com',
    ],
}

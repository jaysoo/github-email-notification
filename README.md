Overview
--------

This standalone server handles POST request from GitHub whenever someone 
does a `git push` to the repo.

For more details, please see GitHub's documentation on [Post-Receive Hooks](http://help.github.com/post-receive-hooks/).

Requirements
------------

* Python 2.5 or later
* [Bottle](http://bottlepy.org/docs/dev/) framework (built using 0.10 dev version).
* simplejson (**if** using Python 2.5)

Configuration
-------------

Modify the `settings.py` file.

	# The hostname and port to listen on
    host = 'localhost'
    port = 8000
    
    # Whitelisted IP that are allowed to access this service
    addr_whitelist = [
        '127.0.0.1',
        
        # GitHub's IP address
        '207.97.227.253',
    ]
    
	# Email sender
    email_from = 'User <user@example.com>'
    
	# List of addresses to send to
    email_to = [
        'user@example.com',
    ]

Running
-------

To start the server, simply run the script!

	./server.py

Setting up on GitHub
--------------------

In your repo's **Service Hooks** section, under admin, go to **Post-Receive URLs**.

Use the host and port that points to your deployed service (e.g. http://example.com:8000/) 
and click **Update Settings**.

You can test the service by clicking on **Test Hook**.

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from _base import BaseConfiguration as Config
from configurations.values import SecretValue
from os.path import join

"""

	NOTE: There is a bug regarding neo4django for Django >= 1.9. The "django.utils.importlib" module was deprecated in
	1.7 and removed in 1.9, making the import fail. Add the following to the file "neo4django/utils.py", line 242 to
	create a workaround:

	try: from django.utils.importlib import import_module
	except ImportError: from importlib import import_module

	Remember to post the fix as a pull request one of these days... 'cause that's what you do when you fix someone
	else's laziness-triggered mistakes.

"""

class Development(Config):

	# Base settings
	DEBUG = True

	# Security settings
	SECRET_KEY = '2!j5*n=5^u+tlrq^d5c52ww*$*c7qgdv&2d*kv$=37rvh%nio6'

	# Databases
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'HOST': 'localhost',
			'NAME': SecretValue(environ_name = 'REL_NAME', environ_prefix = 'RHEA'),
			'USER': SecretValue(environ_name = 'REL_USER', environ_prefix = 'RHEA'),
			'PASSWORD': SecretValue(environ_name = 'REL_PASSWD', environ_prefix = 'RHEA')
		}
	}
	NEO4J_DATABASES = {
		'default': {
			'HOST': 'localhost',
			'PORT': 7474,
			'ENDPOINT': SecretValue(environ_name = 'GRP_ENDPOINT', environ_prefix = 'RHEA')
		}
	}
	DATABASE_ROUTERS = [ 'neo4django.utils.Neo4djangoIntegrationRouter' ]

	# Static files
	STATIC_ROOT = join(Config.BASE_DIR, 'static')

	# Logging
	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'handlers': {
			'file': { 'level': 'DEBUG', 'class': 'logging.FileHandler', 'filename': join(Config.BASE_DIR, 'development.log') }
		},
		'loggers': {
			'django': {
				'handlers': [ 'file' ],
				'level': 'DEBUG',
				'propagate': True
			}
		}
	}
class Testing(Config):

	# Base settings
	DEBUG = True

	# Security settings
	SECRET_KEY = '2!j5*n=5^u+tlrq^d5c52ww*$*c7qgdv&2d*kv$=37rvh%nio6'

	# Databases
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': join(Config.BASE_DIR, 'db.sqlite3'),
			'TEST': { 'NAME': join(Config.BASE_DIR, 'test.sqlite3') }
		}
	}

	# Testing
	TEST_RUNNER = 'django.test.runner.DiscoverRunner'

	# Static files
	STATIC_ROOT = join(Config.BASE_DIR, 'static')

	# Logging
	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'handlers': {
			'file': { 'level': 'DEBUG', 'class': 'logging.FileHandler', 'filename': join(Config.BASE_DIR, 'testing.log') }
		},
		'loggers': {
			'django': {
				'handlers': [ 'file' ],
				'level': 'DEBUG',
				'propagate': True
			}
		}
	}

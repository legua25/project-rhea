# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from _base import BaseConfiguration as Config
from configurations.values import SecretValue
from os.path import join


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

	# Email
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
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

	# Email
	EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os.path import dirname, abspath, join
from configurations import Configuration

class BaseConfiguration(Configuration):

	# Base settings
	BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
	WSGI_APPLICATION = 'rhea.wsgi.application'
	ROOT_URLCONF = 'rhea.urls'

	# Security settings
	ALLOWED_HOSTS = []
	AUTH_PASSWORD_VALIDATORS = [
	    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
	    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
	    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
        { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' }
	]
	AUTH_USER_MODEL = 'rhea.User'

	# Installed applications
	INSTALLED_APPS = [
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'widget_tweaks',
		'imagekit',
		'django_select2',
		'app.rhea'
	]

	# Middleware classes
	MIDDLEWARE_CLASSES = [
		'django.middleware.security.SecurityMiddleware',
		'django.contrib.sessions.middleware.SessionMiddleware',
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.contrib.auth.middleware.AuthenticationMiddleware',
		'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
		'django.contrib.messages.middleware.MessageMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware'
	]

	# Databases
	DATABASES = {
		'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': join(BASE_DIR, 'db.sqlite3') }
	}

	# Templates
	TEMPLATES = [
		{
			'BACKEND': 'django.template.backends.django.DjangoTemplates',
			'DIRS': [],
			'APP_DIRS': True,
			'OPTIONS': {
				'context_processors': [
					'django.template.context_processors.debug',
					'django.template.context_processors.request',
					'django.contrib.auth.context_processors.auth',
					'django.contrib.messages.context_processors.messages'
				]
			}
		}
	]

	# Internationalization (i18n)
	LANGUAGE_CODE = 'en-us'
	TIME_ZONE = 'UTC'
	USE_I18N = True
	USE_L10N = True
	USE_TZ = True

	# Static files
	STATIC_URL = '/static/'
	MEDIA_URL = '/media/'
	MEDIA_ROOT = join(BASE_DIR, 'media')

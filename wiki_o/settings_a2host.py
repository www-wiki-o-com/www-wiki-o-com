"""  __      __    __               ___
    /  \    /  \__|  | _ __        /   \
    \   \/\/   /  |  |/ /  |  __  |  |  |
     \        /|  |    <|  | |__| |  |  |
      \__/\__/ |__|__|__\__|       \___/

A web service for sharing opinions and avoiding arguments

@file       wiki-o/settings.py
@brief      The Django settings file for the main server
@copyright  GNU Public License, 2018
@authors    Frank Imeson
"""

import os
import sys
from .settings_base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Host Config
ALLOWED_HOSTS = ['www.wiki-o.com', 'admin.wiki-o.com', 'wiki-o.com', '75.98.169.10']


# AllAuth Config
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
INVITATIONS_INVITATION_ONLY = True
INVITATIONS_INVITATION_EXPIRY = 14
INVITATIONS_ACCEPT_INVITE_AFTER_SIGNUP = True


# Email setup (postfix)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'accounts@wiki-o.com'
EMAIL_USE_TLS = False


# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file incorporates code covered by the following terms:
#
#     Copyright (c) 2018 Lab Digital
#
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to
#     permit persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#     NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#     BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#     ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#     CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#     SOFTWARE.
import logging

from core.jwt.validator import TokenError, TokenValidator
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

logger = logging.getLogger(__name__)


def authenticate(request):
    """Entrypoint for Django Rest Framework."""
    jwt_token = get_jwt_token(request)
    if jwt_token is None:
        return None

    # Authenticate token
    try:
        token_validator = get_token_validator(request)
        jwt_payload = token_validator.validate(jwt_token)
    except TokenError:
        raise exceptions.AuthenticationFailed()

    return jwt_payload


def get_jwt_token(request):
    auth = get_authorization_header(request).split()
    if not auth or smart_text(auth[0].lower()) != 'bearer':
        return None

    if len(auth) == 1:
        msg = _('Invalid Authorization header. No credentials provided.')
        raise exceptions.AuthenticationFailed(msg)
    elif len(auth) > 2:
        msg = _(
            'Invalid Authorization header. Credentials string '
            'should not contain spaces.'
        )
        raise exceptions.AuthenticationFailed(msg)

    return auth[1]


def get_token_validator(request):
    return TokenValidator(settings.JWKS_ENDPOINT)

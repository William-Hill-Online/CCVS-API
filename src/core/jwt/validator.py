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
import json

import jwt
import requests
from django.utils.functional import cached_property
from jwt.algorithms import RSAAlgorithm


class TokenError(Exception):
    pass


class TokenValidator:
    def __init__(self, jwks_endpoint):
        self.jwks_endpoint = jwks_endpoint

    @cached_property
    def _json_web_keys(self):
        response = requests.get(self.jwks_endpoint + '/.well-known/jwks.json')
        response.raise_for_status()
        json_data = response.json()
        return {item['kid']: json.dumps(item) for item in json_data['keys']}

    def _get_public_key(self, token):
        try:
            headers = jwt.get_unverified_header(token)
        except jwt.DecodeError as exc:
            raise TokenError(str(exc))

        jwk_data = self._json_web_keys.get(headers['kid'])

        if jwk_data:
            return RSAAlgorithm.from_jwk(jwk_data)

    def validate(self, token):
        public_key = self._get_public_key(token)
        if not public_key:
            raise TokenError('No key found for this token')

        try:
            jwt_data = jwt.decode(
                token,
                public_key,
                audience=None,
                issuer=self.jwks_endpoint,
                algorithms=['RS256'],
            )
        except (jwt.InvalidTokenError,
                jwt.ExpiredSignature,
                jwt.DecodeError) as exc:
            raise TokenError(str(exc))
        return jwt_data

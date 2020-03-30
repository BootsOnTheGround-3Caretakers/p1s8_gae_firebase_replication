# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import six
from six import integer_types
from six import text_type as unicode

if len(integer_types) == 1:
    long = integer_types[0]
if six.PY2:
    from google.appengine.api import app_identity

    app_id = unicode(app_identity.get_application_id()).lower()
else:
    import os

    app_id = unicode(os.environ.get('GAE_APPLICATION')).lower()


class PostDataRules(object):
    account_type = [True, unicode, "account_type"]
    object_id = [True, unicode, "greater0", "less<20000"]
    optional_object_id = [False, unicode, "greater0", "less<20000"]
    internal_uid = [True, unicode, "bigint", "greater0"]
    optional_name = [False, unicode, "len<151"]
    optional_description = [False, unicode, "len<1000"]
    optional_number = [False, unicode, "bigint"]
    optional_uid = [False, unicode, "bigint", "greater0"]
    json_encoded_unicode = [True, unicode, "len1", "len<1048480"]
    positive_number = [True, unicode, "bigint", "greater0"]
    required_name = [True, unicode, "len1"]


class GlobalSettings(object):
    post_data_rules = PostDataRules
    project_id = "p1"

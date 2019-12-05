"""
Helper module for the unit test created.
Goal is to DRY the functions.
Functions:
    get_keys: which returns an array from the validation errors
            of the ex_handler
NOTE: This should be use in the test.py ONLY of the applications
"""
import json

CONTENT_TYPE = 'application/json'


def get_keys(res):
    """
    Get the keys from the response object then
    return as a sorted list

    :Parameters:
        res : (json) response object

    :Return:
        list
    """
    keys = sorted([value['err_code'] for value in res.data['detail']])
    if len(keys) == 1:
        keys = keys[0]
    return keys


def get_code(res):
    """
    Get the error status from response object

    :Parameters:
        res: (json) response object

    :Return:
        String
    """
    return res.data['status']


def req_get(testcase, info, url):
    """
    custom request for GET

    :Parameters:
        testcase : (TestCase) self
        info : (dict) GET parameters
        url : (str) request url

    :Return:
        response : Response object
    """

    # token auth
    if hasattr(testcase, 'token'):
        response = testcase.client.get(
            url,
            data=info,
            content_type=CONTENT_TYPE,
            HTTP_AUTHORIZATION='Token ' + testcase.token)
    # anonymous user
    else:
        response = testcase.client.get(
            url,
            data=info,
            content_type=CONTENT_TYPE)

    return response


def req_post(testcase, info, url):
    """
    custom request for POST

    :Parameters:
        tesecase : (TestCase) self
        info : (dict) POST body
        url : (str) request url

    :Return:
        response : Response object
    """

    # key auth (kyc submission)
    if (hasattr(testcase, 'client_id')
            and hasattr(testcase, 'secret')):
        response = testcase.client.post(
            url,
            data=json.dumps(info),
            content_type=CONTENT_TYPE,
            HTTP_CLIENT_ID=testcase.client_id,
            HTTP_SECRET=testcase.secret)
    # token auth
    elif hasattr(testcase, 'token'):
        response = testcase.client.post(
            url,
            data=json.dumps(info),
            content_type=CONTENT_TYPE,
            HTTP_AUTHORIZATION='Token ' + testcase.token)
    # anonymous user
    else:
        response = testcase.client.post(
            url,
            data=json.dumps(info),
            content_type=CONTENT_TYPE)

    return response

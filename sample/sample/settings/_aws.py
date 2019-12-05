"""
For AWS settings, put the credentials here.
"""
import os

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None
AWS_STORAGE_BUCKET_NAME = ''
AWS_S3_CUSTOM_DOMAIN = '%s.s3-ap-northeast-1.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400',}
AWS_S3_DEFAULT_REGION = 'ap-northeast-1'
AWS_LOCATION = 'media'
AWS_DEFAULT_ACL = 'private'
MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
MEDIA_ROOT = os.path.join(os.path.abspath('.'), 'media')
DEFAULT_FILE_STORAGE = 'sample.settings.storage_media.MediaStorage'
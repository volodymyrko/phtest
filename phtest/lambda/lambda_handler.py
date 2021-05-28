import os
import uuid

import boto3

from phtest_utils.utils import validate, generate_response
from phtest_utils.validation_models import (
    GetAllAnnouncementsModel, PostAnnouncementModel
)


DATE_FORMAT = '%Y-%m-%d'
NOT_FOUND_RESPONSE = {
    'status_code': 404,
    'body': {'error': 'Object not found'},
}

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['DDB_TABLE_NAME'])


@generate_response
@validate(GetAllAnnouncementsModel)
def announcements(event, context, validated_data):
    kwargs = {}

    if validated_data.get('limit'):
        kwargs['Limit'] = validated_data['limit']

    if validated_data.get('last_evaluated_key'):
        kwargs['ExclusiveStartKey'] = {
            'uuid': validated_data['last_evaluated_key']
        }

    req = table.scan(**kwargs)

    data = {
        'items': req.get('Items', []),
    }

    if 'LastEvaluatedKey' in req:
        data['last_evaluated_key'] = req['LastEvaluatedKey']['uuid']

    return {'body': data}


@generate_response
def get_announcement(event, context):
    announcement_uuid = event['pathParameters']['uuid']
    obj = table.get_item(Key={'uuid': announcement_uuid}).get('Item')

    return {'body': obj} if obj else NOT_FOUND_RESPONSE


@generate_response
@validate(PostAnnouncementModel)
def post_announcement(event, context, validated_data):
    data = {
        'uuid': str(uuid.uuid4()),
        'name': validated_data['name'],
        'description': validated_data['description'],
        'date': validated_data['date'].strftime(DATE_FORMAT)
    }

    table.put_item(Item=data)

    return {'body': data, 'status_code': 201}

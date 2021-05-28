import json
from json.decoder import JSONDecodeError

from pydantic import ValidationError


HEADERS = {
    'Content-Type': 'application/json',
    'access-control-allow-origin': '*',
    'access-control-allow-headers': 'Content-Type,Origin,Accept,X-Requested-With,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
    'access-control-allow-methods': 'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD',
    'access-control-allow-credentials': 'true',
}


def validate(validation_model):
    """Validate input data."""
    def wrap(func):
        def wrapped(event, context):
            if event['httpMethod'] == 'GET':
                data = event.get('queryStringParameters') or {}
            else:  # POST
                try:
                    data = json.loads(event.get('body') or '{}')
                except JSONDecodeError:
                    return {
                        'status_code': 400,
                        'body': {'error': 'invalid request body'}
                    }

            try:
                item = validation_model(**data)
            except ValidationError as exc:
                return {
                    'status_code': 400,
                    'body': {'error': exc.errors()}
                }

            return func(event, context, item.dict())

        return wrapped

    return wrap


def generate_response(func):
    """Generate required for apigw format based on func output."""
    def wrapped(*args, **kwargs):
        lambda_response = func(*args, **kwargs)

        response = {
            'statusCode': lambda_response.get('status_code', 200),
            'headers': HEADERS,
        }

        if lambda_response.get('body'):
            response['body'] = json.dumps(lambda_response['body'])

        return response

    return wrapped

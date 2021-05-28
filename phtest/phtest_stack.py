import os
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_apigateway as apigw
import aws_cdk.aws_dynamodb as ddb
from aws_cdk import core as cdk
from aws_cdk.aws_lambda_python import PythonFunction, PythonLayerVersion


dir_path = os.path.dirname(os.path.realpath(__file__))
lamda_dir = os.path.join(dir_path, 'lambda')
phtest_src = os.path.join(dir_path, 'phtest_src')


class PhtestStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # dynamodb
        table = ddb.Table(
            self, 'DDB Announcements',
            partition_key={'name': 'uuid', 'type': ddb.AttributeType.STRING},
            read_capacity=3,
            write_capacity=3,
        )

        # lambda
        python_layers = [PythonLayerVersion(self, 'PhTestUtils', entry=phtest_src)]
        announcements_fn = PythonFunction(
            self,
            'AnnouncementFunction',
            entry=lamda_dir,
            index='lambda_handler.py',
            handler='announcements',
            runtime=_lambda.Runtime.PYTHON_3_7,
            layers=python_layers,
            environment={
                'DDB_TABLE_NAME': table.table_name,
            }
        )
        get_announcement_fn = PythonFunction(
            self,
            'GETAnnouncement',
            entry=lamda_dir,
            index='lambda_handler.py',
            handler='get_announcement',
            runtime=_lambda.Runtime.PYTHON_3_7,
            layers=python_layers,
            environment={
                'DDB_TABLE_NAME': table.table_name,
            }
        )
        post_announcement_fn = PythonFunction(
            self,
            'POSTAnnouncement',
            entry=lamda_dir,
            index='lambda_handler.py',
            handler='post_announcement',
            runtime=_lambda.Runtime.PYTHON_3_7,
            layers=python_layers,
            environment={
                'DDB_TABLE_NAME': table.table_name,
            }
        )

        # add permisiions
        table.grant_read_write_data(announcements_fn)
        table.grant_read_write_data(post_announcement_fn)
        table.grant_read_write_data(get_announcement_fn)

        # lambda integrations
        announcements_int = apigw.LambdaIntegration(announcements_fn)
        post_announcement_int = apigw.LambdaIntegration(post_announcement_fn)
        get_announcement_int = apigw.LambdaIntegration(get_announcement_fn)

        # apigw
        cors_options = apigw.CorsOptions(
            allow_origins=['*'],
            allow_credentials=True
        )
        api = apigw.RestApi(
            self,
            'ApiGateway',
            rest_api_name='ApiGateway',
            default_cors_preflight_options=cors_options,
        )

        announcements_resource = api.root.add_resource('announcements')
        announcements_resource.add_method('GET', announcements_int)
        announcements_resource.add_method('POST', post_announcement_int)

        ann_obj_resource = announcements_resource.add_resource('{uuid}')
        ann_obj_resource.add_method('GET', get_announcement_int)

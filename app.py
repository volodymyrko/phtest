#!/usr/bin/env python3
import os

from aws_cdk import core

from phtest.phtest_stack import PhtestStack


app = core.App()
PhtestStack(app, "PhtestStack",
    env=core.Environment(
        account=os.environ['AWS_ACCOUNT_ID'],
        region=os.environ['AWS_REGION'],
    ),
)

app.synth()

from flask import Flask, render_template, url_for, request, session, redirect, make_response, sessions
import flask_jwt_extended
from flask_jwt_extended.utils import set_access_cookies
from flask_jwt_extended.view_decorators import verify_jwt_in_request

from werkzeug.wrappers import response

import botocore
import boto3
from boto3 import Session

import time
import random
import string

from flask_awscognito import AWSCognitoAuthentication

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
jwt = JWTManager(app)

flask_jwt_extended.jwt_required(optional=False, fresh=False, refresh=False, locations=None)
app.config['AWS_DEFAULT_REGION'] = 'eu-central-1'
app.config['AWS_COGNITO_DOMAIN'] = 'juun.co'
app.config['AWS_COGNITO_USER_POOL_ID'] = 'eu-central-1_fpgMIOWgs'
app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '40a0485tsh6tgk1r0ad72rafj7'
app.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = '1au9rspdrmcrb9r0502p2jk8cd58gid82crhpkak1ggoefpi4q0f'
app.config['AWS_COGNITO_REDIRECT_URL'] = 'https://juun.co/loggedin'

aws_auth = AWSCognitoAuthentication(app)
#login config
from celery import Celery

app.config.update(SECRET_KEY='???+(?&?2-C?J?>', ENV='production')
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['0.0.0.0:443'],
        broker=app.config['0.0.0.0:443']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
dynamodb = boto3.resource('dynamodb', aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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', region_name='eu-central-1')

table = dynamodb.Table('users')

s3 = boto3.resource('s3', aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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')
letters = string.ascii_lowercase
ACCESS_KEY = "AKIAUBLQ6V2IFEHUERNB"
SECRET_KEY = "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"
REGION_NAME = "eu-central-1"
BUCKET_NAME = "tts-buck"


def create_url():

  print("Using bucket: " + BUCKET_NAME)
  ses = Session(aws_access_key_id='AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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',region_name='eu-central-1')
  client = ses.client('s3',aws_access_key_id='AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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')
  objs = client.list_objects(Bucket=BUCKET_NAME)['Contents']     
  latest = max(objs, key=lambda x: x['LastModified'])
  url = client.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': BUCKET_NAME,
        'Key': latest['Key']
    },
    ExpiresIn=604799
  )
  return url


def synth_speech(form):

  ses = Session(aws_access_key_id=ACCESS_KEY,
              aws_secret_access_key=SECRET_KEY,
              region_name=REGION_NAME)

  client = ses.client('s3')
  neuralnames = ["Olivia","Amy","Emma","Brian","Aria","Ayanda","Ivy","Joanna","Kendra","Kimberly","Salli","Joey","Justin","Kevin","Matthew","Gabrielle","Léa","Vicki","Bianca","Takumi","Seoyeon","Camila","Lucia","Lupe"]
  recievedtext = request.form['text-input']
  language = request.form['Language']
  engineusing = ""
  print("Text recieved...")
  if language in neuralnames:
    engineusing = "neural"
    print("Using the neural engine")
  else:
    print("Using the standard engine")
    engineusing = "standard"
  print(s3.Bucket(BUCKET_NAME) in s3.buckets.all())
  polly_client = boto3.Session(aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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', region_name=REGION_NAME).client('polly')
  task = polly_client.start_speech_synthesis_task(VoiceId=language, OutputFormat='mp3', Text = recievedtext, Engine = engineusing, OutputS3BucketName = BUCKET_NAME, SnsTopicArn = "arn:aws:sns:eu-central-1:277799153296:TTS-Status")
  taskId = task['SynthesisTask']['TaskId']
  finished = False
  print( "Task id is {} ".format(taskId))
  task_status = polly_client.get_speech_synthesis_task(TaskId = taskId)
  print(task_status['SynthesisTask']['TaskStatus'])
  while(True):
    taskId = task['SynthesisTask']['TaskId']
    task_status = polly_client.get_speech_synthesis_task(TaskId = taskId)
    if task_status['SynthesisTask']['TaskStatus'] == "completed":
      print("Task finished!")
      finished = True
      break
  print(task_status)
  if finished == True:
    return create_url()
print("Done...")

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
  



@app.route('/')
def login():
  return redirect("https://juunlogin.auth.eu-central-1.amazoncognito.com/login?response_type=code&client_id=40a0485tsh6tgk1r0ad72rafj7&redirect_uri=https%3A%2F%2Fjuun.co%2Fhome", code=302)

@app.route('/', methods=['GET', 'POST'])
def check():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    table = dynamodb.Table('users')

    response = table.get_item(Key={'UserID': username})
    response2 = table.get_item(Key={'password': password})
    name = username
  if response['Item'] and response2['Item']:
    print('login found.')
    return render_template('index.html', name = name)
  else:
    print('login not found')
    return render_template('login.html')
@app.route('/home', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
      form = request.form
      result = synth_speech(form)
      resp = render_template('index.html', url = result)
    verify_jwt_in_request()
    if get_jwt_identity():
      return resp
    else:
      return redirect(aws_auth.get_sign_in_url())
    



@app.route("/loggedin", methods=["GET"])
def logged_in():
    access_token = aws_auth.get_access_token(request.args)
    resp = make_response(redirect(url_for("protected")))
    set_access_cookies(resp, access_token, max_age=30 * 60)
    return resp

if __name__ == "__main__":
  context = ('certificate.crt', 'private.key')
  app.run(debug=False, host="0.0.0.0", port="443", ssl_context=context)



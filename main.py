
#Import Flask and all its dependencies.
from flask import Flask, render_template, url_for, request, session, redirect, make_response, sessions,jsonify
import flask_jwt_extended
from flask_jwt_extended.utils import set_access_cookies
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from werkzeug.wrappers import response

#Import boto3 package.
import botocore
import boto3
from boto3 import Session

#Import packages for string generation.
import time
import random
import string

#Import Flask Cognito Extension
from flask_cognito_auth import CognitoAuthManager
from flask_cognito_auth import login_handler
from flask_cognito_auth import logout_handler
from flask_cognito_auth import callback_handler

#Import Flask JWT Extension
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
jwt = JWTManager(app)

# Setup the flask-cognito-auth extension
app.config['COGNITO_REGION'] = "eu-central-1"
app.config['COGNITO_USER_POOL_ID'] = "eu-central-1_fpgMIOWgs"
app.config['COGNITO_CLIENT_ID'] = "40a0485tsh6tgk1r0ad72rafj7"
app.config['COGNITO_CLIENT_SECRET'] = "1au9rspdrmcrb9r0502p2jk8cd58gid82crhpkak1ggoefpi4q0f"
app.config['COGNITO_DOMAIN'] = "https://juun.co"


app.config['COGNITO_REDIRECT_URI'] = "https://yourdomainhere/cognito/callback"  # Specify this url in Callback URLs section of Appllication client settings of User Pool within AWS Cognito Sevice. Post login application will redirect to this URL

app.config['COGNITO_SIGNOUT_URI'] = "https://yourdomainhere/login"

app.config.update(SECRET_KEY='???+(?&?2-C?J?>', ENV='production')

cognito = CognitoAuthManager(app)

#login config
from celery import Celery

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
  print("Do the stuff before login to AWS Cognito Service")
  response = redirect(url_for("cognitologin"))
  return response

@app.route('/logout')
def logout():
  print("Do the stuff before logout from AWS Cognito Service")
  response = redirect(url_for("cognitologout"))
  return response

@app.route('/cognito/login', methods=['GET'])
@login_handler
def cognitologin():
    pass

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
    current_user = session["username"]
    return jsonify(logged_in_as=current_user), 200, resp
    
@app.route('/cognito/callback', methods=['GET'])
@callback_handler
def callback():
    print("Do the stuff before post successfull login to AWS Cognito Service")
    for key in list(session.keys()):
        print(f"Value for {key} is {session[key]}")
    response = redirect(url_for("home"))
    return response

@app.route('/cognito/logout', methods=['GET'])
@logout_handler
def cognitologout():
    pass

@app.route('/page500', methods=['GET'])
def page500():
    return jsonify(Error="Something went wrong"), 500


if __name__ == "__main__":
  context = ('certificate.crt', 'private.key')
  app.run(debug=False, host="0.0.0.0", port="443", ssl_context=context)



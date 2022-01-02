
from flask import Flask, render_template, url_for, request, session, redirect, abort
from werkzeug.datastructures import _CacheControl, Authorization
from werkzeug.wrappers import response
import botocore
import boto3
from boto3 import Session
import time
import random
import string
from flask_awscognito import AWSCognitoAuthentication
import os
import pathlib
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
app = Flask(__name__)
app.config.update(SECRET_KEY='???+(?&?2-C?J?>', ENV='production')

#Google auth shit
loggedin = False
GOOGLE_CLIENT_ID = "701515876447-76h7m4tj3cojl1b74b0hrtuafnhk247q.apps.googleusercontent.com"
client_secret_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
  client_secrets_file=client_secret_file,
  scopes=['https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/userinfo.email', "openid"],
  redirect_uri="https://juun.co/callback"
)

def login_is_required(func):
  def wrapper(*args, **kwargs):
    if "google_id" not in session:
      redirect("https://juun.co/login", 401) #Auth required
    else:
      Loggedin = True
      return function()
  wrapper.__name__ = func.__name__    
  return wrapper


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


@app.route('/callback')
def callback():
  flow.fetch_token(authorization_response=request.url)

  if not session['state'] == request.args['state']:
    abort(500)
  credentials = flow.credentials
  request_session = request.session()
  cached_session =  cachecontrol.CacheControl(request_session)
  token_request = google.auth.transport.requests.Request(session=cached_session)

  id_info = id_token.verify.oauth2_token(
    id_token =credentials._id_token,
    request = token_request,
    audience =GOOGLE_CLIENT_ID 
    
  )
  session['google_id'] = id_info.get('sub')
  session['name'] = id_info.get('name')
  return redirect('/')
@app.route('/login')
def login():
  authorization_url, state = flow.authorization_url()
  session['state'] = state
  return redirect(authorization_url)


@app.route('/', methods=['GET', 'POST'])
@login_is_required
def index():
    result = "Nothing"
    if request.method == 'POST':
      form = request.form
      result = synth_speech(form)
    return render_template('index.html', url = result)



if __name__ == "__main__":
  context = ('certificate.crt', 'private.key')
  app.run(debug=False, host="0.0.0.0", port="443", ssl_context=context)

from flask import Flask, render_template, url_for, request
from werkzeug.wrappers import response

import botocore
import boto3
from boto3 import Session
import time
import random
import string
#login config

app = Flask(__name__)

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


  



@app.route('/')
def login():
  return render_template('login.html')

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

    return render_template('index.html', url = result)


if __name__ == "__main__":
  context = ('certificate.crt', 'private.key')
  app.run(debug=False, host="0.0.0.0", port="443", ssl_context=context)
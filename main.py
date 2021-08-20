from flask import Flask, render_template, url_for, request
from werkzeug.wrappers import response
app = Flask(__name__)
import botocore
import boto3
from boto3 import Session
import time
import random
import string
#login config

dynamodb = boto3.resource('dynamodb', aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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', region_name='eu-central-1')

table = dynamodb.Table('users')

s3 = boto3.resource('s3', aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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')
letters = string.ascii_lowercase
ACCESS_KEY = "AKIAUBLQ6V2IFEHUERNB"
SECRET_KEY = "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"
REGION_NAME = "eu-central-1"
# BUCKET_NAME = ''.join(random.choice(letters) for i in range(10))
BUCKET_NAME = "tts-buck"
print(BUCKET_NAME)



def create_url():

  print(BUCKET_NAME)
  ses = Session(aws_access_key_id='AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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',region_name='eu-central-1')
  client = ses.client('s3',aws_access_key_id='AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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')
  time.sleep(40)
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
  recievedtext = request.form['text-input']
  print("text recieved")
  #client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={
  #      'LocationConstraint': 'ca-central-1'
  #  },
    
  #  GrantFullControl="id=c3c480d6de740e9b3ce03f0ef553a87da759a441329d4a67f7558be00fe3d6bb",
  #  ObjectLockEnabledForBucket=False
    
  #)
  print(s3.Bucket(BUCKET_NAME) in s3.buckets.all())
  polly_client = boto3.Session(aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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', region_name=REGION_NAME).client('polly')
  #polly_client.synthesize_speech(VoiceId='Brian', OutputFormat='mp3', Text = recievedtext, Engine = 'neural')
  task = polly_client.start_speech_synthesis_task(VoiceId='Brian', OutputFormat='mp3', Text = recievedtext, Engine = 'neural', OutputS3BucketName = BUCKET_NAME, SnsTopicArn = "arn:aws:sns:eu-central-1:277799153296:TTS-Status")

  print("Call returned: ", task)
  if task['ResponseMetadata']['HTTPStatusCode'] == 200:
    time.sleep(20)
    return create_url()
  else:
    print("Error while calling speech synthesis: ", task)
  print("finished")
  return None



  



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
  app.run(debug=True, host="0.0.0.0", port="80")
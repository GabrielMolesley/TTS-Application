from flask import Flask, render_template, url_for, request
app = Flask(__name__)
import boto3
from boto3 import Session
import time
import random
import string

s3 = boto3.resource('s3', aws_access_key_id= 'AKIAUBLQ6V2IDFCDVKI3', aws_secret_access_key='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')
letters = string.ascii_lowercase
ACCESS_KEY = "AKIAUBLQ6V2IDFCDVKI3"
SECRET_KEY = "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"
REGION_NAME = "eu-central-1"
BUCKET_NAME = ''.join(random.choice(letters) for i in range(10))
print(BUCKET_NAME)



def create_url():


  print(BUCKET_NAME)

  

  ses = Session(aws_access_key_id=ACCESS_KEY,
              aws_secret_access_key=SECRET_KEY,
              region_name=REGION_NAME)
  client = ses.client('s3')
  time.sleep(10)
  objs = client.list_objects(Bucket=BUCKET_NAME)['Contents']     
  latest = max(objs, key=lambda x: x['LastModified'])

  url = client.generate_presigned_url(
    ClientMethod='get_object',
    Params={
        'Bucket': BUCKET_NAME,
        'Key': latest['Key']
    },
    ExpiresIn=600
  )
  #deleteresponse = client.delete_bucket(
    #Bucket=BUCKET_NAME,
  #print(deleteresponse)
  return url


def synth_speech(form):

  ses = Session(aws_access_key_id=ACCESS_KEY,
              aws_secret_access_key=SECRET_KEY,
              region_name=REGION_NAME)

  client = ses.client('s3')
  recievedtext = request.form['text-input']
  print("text recieved")
  client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={
        'LocationConstraint': 'eu-central-1'
    },
    
    GrantFullControl="id=c3c480d6de740e9b3ce03f0ef553a87da759a441329d4a67f7558be00fe3d6bb",
    ObjectLockEnabledForBucket=False
    
  )
  print(s3.Bucket(BUCKET_NAME) in s3.buckets.all())
  polly_client = boto3.Session(aws_access_key_id= 'AKIAUBLQ6V2IDFCDVKI3', aws_secret_access_key='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', region_name=REGION_NAME).client('polly', )
  polly_client.synthesize_speech(VoiceId='Brian', OutputFormat='mp3', Text = recievedtext, Engine = 'neural')
  task = polly_client.start_speech_synthesis_task(VoiceId='Brian', OutputFormat='mp3', Text = recievedtext, Engine = 'neural', OutputS3BucketName = BUCKET_NAME, SnsTopicArn = "arn:aws:sns:eu-central-1:277799153296:TTS-Status")

  print("Call returned: ", task)
  if task['ResponseMetadata']['HTTPStatusCode'] == 200:
    time.sleep(20)
    return create_url()
  else:
    print("Error while calling speech synthesis: ", task)
  print("finished")
  return None



  


  print("succesvoll")
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
      form = request.form
      result = synth_speech(form)

    return render_template('index.html', url = result)



if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", threaded=True)



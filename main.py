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
from OpenSSL import SSL

context = SSL.Context(SSL.TLSv1_2_METHOD)
context.use_certificate_file('''-----BEGIN CERTIFICATE-----
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
13+yBMde/jcLf6kzsoFO
-----END CERTIFICATE-----''')
context.use_certificate_chain('''-----BEGIN CERTIFICATE-----
MIIG1TCCBL2gAwIBAgIQbFWr29AHksedBwzYEZ7WvzANBgkqhkiG9w0BAQwFADCB
iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl
cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV
BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMjAw
MTMwMDAwMDAwWhcNMzAwMTI5MjM1OTU5WjBLMQswCQYDVQQGEwJBVDEQMA4GA1UE
ChMHWmVyb1NTTDEqMCgGA1UEAxMhWmVyb1NTTCBSU0EgRG9tYWluIFNlY3VyZSBT
aXRlIENBMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAhmlzfqO1Mdgj
4W3dpBPTVBX1AuvcAyG1fl0dUnw/MeueCWzRWTheZ35LVo91kLI3DDVaZKW+TBAs
JBjEbYmMwcWSTWYCg5334SF0+ctDAsFxsX+rTDh9kSrG/4mp6OShubLaEIUJiZo4
t873TuSd0Wj5DWt3DtpAG8T35l/v+xrN8ub8PSSoX5Vkgw+jWf4KQtNvUFLDq8mF
WhUnPL6jHAADXpvs4lTNYwOtx9yQtbpxwSt7QJY1+ICrmRJB6BuKRt/jfDJF9Jsc
RQVlHIxQdKAJl7oaVnXgDkqtk2qddd3kCDXd74gv813G91z7CjsGyJ93oJIlNS3U
gFbD6V54JMgZ3rSmotYbz98oZxX7MKbtCm1aJ/q+hTv2YK1yMxrnfcieKmOYBbFD
hnW5O6RMA703dBK92j6XRN2EttLkQuujZgy+jXRKtaWMIlkNkWJmOiHmErQngHvt
iNkIcjJumq1ddFX4iaTI40a6zgvIBtxFeDs2RfcaH73er7ctNUUqgQT5rFgJhMmF
x76rQgB5OZUkodb5k2ex7P+Gu4J86bS15094UuYcV09hVeknmTh5Ex9CBKipLS2W
2wKBakf+aVYnNCU6S0nASqt2xrZpGC1v7v6DhuepyyJtn3qSV2PoBiU5Sql+aARp
wUibQMGm44gjyNDqDlVp+ShLQlUH9x8CAwEAAaOCAXUwggFxMB8GA1UdIwQYMBaA
FFN5v1qqK0rPVIDh2JvAnfKyA2bLMB0GA1UdDgQWBBTI2XhootkZaNU9ct5fCj7c
tYaGpjAOBgNVHQ8BAf8EBAMCAYYwEgYDVR0TAQH/BAgwBgEB/wIBADAdBgNVHSUE
FjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwIgYDVR0gBBswGTANBgsrBgEEAbIxAQIC
TjAIBgZngQwBAgEwUAYDVR0fBEkwRzBFoEOgQYY/aHR0cDovL2NybC51c2VydHJ1
c3QuY29tL1VTRVJUcnVzdFJTQUNlcnRpZmljYXRpb25BdXRob3JpdHkuY3JsMHYG
CCsGAQUFBwEBBGowaDA/BggrBgEFBQcwAoYzaHR0cDovL2NydC51c2VydHJ1c3Qu
Y29tL1VTRVJUcnVzdFJTQUFkZFRydXN0Q0EuY3J0MCUGCCsGAQUFBzABhhlodHRw
Oi8vb2NzcC51c2VydHJ1c3QuY29tMA0GCSqGSIb3DQEBDAUAA4ICAQAVDwoIzQDV
ercT0eYqZjBNJ8VNWwVFlQOtZERqn5iWnEVaLZZdzxlbvz2Fx0ExUNuUEgYkIVM4
YocKkCQ7hO5noicoq/DrEYH5IuNcuW1I8JJZ9DLuB1fYvIHlZ2JG46iNbVKA3ygA
Ez86RvDQlt2C494qqPVItRjrz9YlJEGT0DrttyApq0YLFDzf+Z1pkMhh7c+7fXeJ
qmIhfJpduKc8HEQkYQQShen426S3H0JrIAbKcBCiyYFuOhfyvuwVCFDfFvrjADjd
4jX1uQXd161IyFRbm89s2Oj5oU1wDYz5sx+hoCuh6lSs+/uPuWomIq3y1GDFNafW
+LsHBU16lQo5Q2yh25laQsKRgyPmMpHJ98edm6y2sHUabASmRHxvGiuwwE25aDU0
2SAeepyImJ2CzB80YG7WxlynHqNhpE7xfC7PzQlLgmfEHdU+tHFeQazRQnrFkW2W
kqRGIq7cKRnyypvjPMkjeiV9lRdAM9fSJvsB3svUuu1coIG1xxI1yegoGM4r5QP4
RGIVvYaiI76C0djoSbQ/dkIUUXQuB8AL5jyH34g3BZaaXyvpmnV4ilppMXVAnAYG
ON51WhJ6W0xNdNJwzYASZYH+tmCWI+N60Gv2NNMGHwMZ7e9bXgzUCZH5FaBFDGR5
S9VWqHB73Q+OyIVvIbKYcSc2w/aSuFKGSA==
-----END CERTIFICATE-----
''')
context.use_privatekey_file('''-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEAxSmnK8qnNAD62mIcS9nTZW6wdSfwhk1WSYAOL47/kaX5yLCC
XzD93TJ93YKBPmOx8hWaTdpBSEoa5eLW6nehkFr5UreQ8dt98KDxOhgEC77gvQ2p
MhNGGfVYRgnvpr2PIxM/8DlTVd3wP5s0XwKxHKHptHFwXLiwFptqOosGq+Nwk653
vX0JUDq5rwWuooTtLBZxAQu64eFPWg/HJ7RLziw1gewtfvKD0uQjHyMF2/V3dMrw
Da15L/KQ0xiNQXaYPPci9YBOknL4iW/wTaaRDEmTaC5VLelCCz8WNapN5QuZJNgV
RwIaVSEizhsBDPze9+e9TedyJz6BlQtXVJV+lwIDAQABAoIBAQCLqzgrg4HzCwap
kXruGL7ySfli5Qo0ebC4nKhv9GMDcIqEKtYQTQppmg0j0AFyivlRvw/yOryoUya+
13Tb4CdptaiNelCJpK2QutJoDv8+utdF1dmYCaNNXEpOQ1erzPkLJeXTbSil2XUJ
+g6dh7Cj0edW1k18wbCsMyiLlFUDifqzKgEP+0373nIEkOz4tIHY+nKegnlbFF/+
IcT5wppuGQ2U6Ka7OuWgqRbGvhihYwYgvbnE4+EUC2Wv0Yf79H5d2ee/sWi43lFQ
p9vNfJZK0QoqG9zkqwbfYrClwf3I9oUyWha7NklTWV5wNan1MBiEAmm7POw+G0xj
2nzsNSrhAoGBAOKCGloxS5CG8t5aoUwkGueqXso0ZrBApux2+QyfHGwQQBs0bRSG
919CIrutzPhPZ0UrRG6kfxU6EfIu5vhrUtBmM3t+B6wXdE5HkSI2P9pbGPr/8GGb
G2r4g7Holp71sju7z4Slrh6EmB94COYP6gXYiPfRIy4xI5CUblhUHtH/AoGBAN7V
alEgiG4gXmvZmQlSK+ViVEcZ/b4vHqTpJQa4POOyek2vDTL/AhMtHzEeRCKo+jAx
cL5tVG1hCW0HhNXLyBQZBVR1d/4la6J87nOhPej+2tV27nnZ5JgTxWTwMWg6LKe/
TQApzDYUQZV5fjnaIrsDwuB0GEVbNEgeoKGTxKNpAoGBAL1hwDzG2II3gprMte3e
hixKM0TnOTCGbcpp0uNtqSrlD2RvmgA+tFeOCVJYB3dZlGOtwGKt4J9T1StjcbQk
r7IUsVjAUBPf7FuC1OMA7rRX1HQQR+Cj+fGfZST77etsTCBLcD9c808K19H/35jT
l3xZxnNFBiAZ771zjSsG8lnrAoGAJsPHuA9JzKay5l43Yki6PDBr6uaZnuFBmny4
pT+d0Bq3bhY63JlCOiXKXFggkEsHIyUmsOoCGvkbk60QLcVCrERiCfxZgIvv+pdz
QAhX5dWYKjSDbg062D3wRAwI/FHKfPAprBKZZPsHIcK988B/9DrGRxfLNR2Vrcou
NY2oUqkCgYEAzsT0u+a2gFRcr0pA1ljjAsE5Edui/t/bcU+iCHInk3C8/gxiosn4
Qruqfwr0Ur9/1DImUyJgUcmRba9UWWFGiEQ0CCcX+Q84qC4XJSCScnp3PmucYtj8
qAA79Km2/fZZQI+LN7vom9bFTNXMnnLkFLao3cRMPfmhGFH5sIjzM8k=
-----END RSA PRIVATE KEY-----''')
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
  neural = ""
  print("text recieved")
  if language in neuralnames:
    neural = "neural"
    print("Using:" + neural)
  else:
    neural = "standard"
    print("Using:" + neural)
  print("text recieved")
  
  #)
  print(s3.Bucket(BUCKET_NAME) in s3.buckets.all())
  polly_client = boto3.Session(aws_access_key_id= 'AKIAUBLQ6V2IFEHUERNB', aws_secret_access_key='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', region_name=REGION_NAME).client('polly')
  #polly_client.synthesize_speech(VoiceId='Brian', OutputFormat='mp3', Text = recievedtext, Engine = 'neural')
  task = polly_client.start_speech_synthesis_task(VoiceId=language, OutputFormat='mp3', Text = recievedtext, Engine = neural, OutputS3BucketName = BUCKET_NAME, SnsTopicArn = "arn:aws:sns:eu-central-1:277799153296:TTS-Status")
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
  print("Call returned: ", task)
print("finished")
#if task['ResponseMetadata']['HTTPStatusCode'] == 200:
    #time.sleep(20)
    #return create_url()

  



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
  app.run(debug=True, host="0.0.0.0", port="80", ssl_context=context)
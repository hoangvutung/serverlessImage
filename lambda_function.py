import json
import boto3
import base64
import PIL
from PIL import Image
from io import BytesIO

s3 = boto3.client('s3')
S3_BUCKET_NAME = 'lab2022serverless'
GET_PATH = "/getImage"
POST_PATH = "/putImage"
RESIZE_PATH= "/resize"
cold_start = True
counter = 1
def lambda_handler(event, context):
    global counter
    global cold_start
    if cold_start:
        listObject = s3.list_objects_v2(Bucket = S3_BUCKET_NAME)
        counter = int(listObject['KeyCount'])
        cold_start = False
    if event['rawPath'] == GET_PATH:
        #Get image from s3 by id 
        id = int(event['queryStringParameters']['id'])
        if id < counter:
            fileName  = str(id) + '.jpg'
            fileObj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=fileName)
            file_content = fileObj["Body"].read()
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/jpg",
                    "Content-Disposition": "attachment; filename={}".format(fileName)
                },
                "body": base64.b64encode(file_content),
                "isBase64Encoded": True
            }
            
        else:
            return {
                'statusCode': 200,
                'body': json.dumps('The image ID is not found!')
            }
    elif event['rawPath'] == POST_PATH:
        #Put image to s3
        file_content = base64.b64decode(event['body'].encode('UTF-8'))
        #file_content = BytesIO(bytes(event["body"], "utf-8")).getbuffer().nbytes
        fileName = str(counter) + '.jpg'
        s3_response = s3.put_object(Bucket=S3_BUCKET_NAME, Key=fileName, Body=file_content)
        counter += 1
        return {
            'statusCode': 200,
            'body': json.dumps('Put image sucessfully! Image ID: '+ str(counter-1))
        }
    elif event['rawPath'] == RESIZE_PATH:
        #resize image by id
        id = int(event['queryStringParameters']['id'])
        w = int(event['queryStringParameters']['w'])
        h = int(event['queryStringParameters']['h'])
        newSize = (w,h)
        if id < counter:
            fileName  = str(id) + '.jpg'
            fileObj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=fileName)
            file_content = fileObj["Body"].read()
            img = Image.open(BytesIO(file_content))
            img = img.resize( newSize, PIL.Image.ANTIALIAS)
            buffer = BytesIO()
            img.save(buffer, 'JPEG')
            buffer.seek(0)
            newFileName = str(counter) + ".jpg"
            obj = s3.put_object( Bucket=S3_BUCKET_NAME, Key=newFileName,Body=buffer)
            counter += 1
            return {
                'statusCode': 200,
                'body': json.dumps('The new image id: '+str(counter-1))
            }

        else:
            return {
                'statusCode': 200,
                'body': json.dumps('The image ID is not found!')
            }

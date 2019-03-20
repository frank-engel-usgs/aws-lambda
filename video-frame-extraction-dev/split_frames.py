from __future__ import print_function

import boto3
import os
import sys
import uuid
import cv2

globalVars  = {}
globalVars['REGION_NAME']           = "us-west-2"
globalVars['tagName']               = "fle-lambda-dev"
globalVars['S3-SourceBucketName']   = "surfboard-rpi"
globalVars['S3-DestBucketName']     = "surfboard-output"

s3Client = boto3.client('s3')

def extractFrames(video_source_path, frame_destination_path):
    os.mkdir(frame_destination_path)
 
    cap = cv2.VideoCapture(video_source_path)
    count = 0
 
    while (cap.isOpened()):
 
        # Capture frame-by-frame
        ret, frame = cap.read()
 
        if ret == True:
            print('Read %d frame: ' % count, ret)
			# save frame as JPEG file
            cv2.imwrite(os.path.join(frame_destination_path, "frame{:d}.jpg".format(count)), frame)  
            count += 1
        else:
            break
 
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
 
def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}/{}'.format(uuid.uuid4(), key)
        upload_path = '/tmp/frames-{}'.format(key)
        
        s3Client.download_file(globalVars['S3-SourceBucketName'], key, download_path)
        fname=key.rsplit('.', 1)[0]
        fextension=key.rsplit('.', 1)[1]

        extractFrames(download_path, upload_path)
        s3Client.upload_file(upload_path, globalVars['S3-DestBucketName'], 'frames/{0}-frame.{1}'.format(fname,fextension))       
    return key

if __name__ == "__main__":
	handler(42, 42)

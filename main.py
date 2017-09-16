import boto3
#import picamera
import numpy as np
import cv2
import time

s3 = boto3.resource('s3')
client = boto3.client('rekognition')


def upload_image(source_file, photo_bucket):
    s3.meta.client.upload_file(source_file, photo_bucket, source_file)


def delete_image(photo_bucket, key):
    s3.Bucket(photo_bucket).delete_objects(
        Delete={
            'Objects': [
                {
                    'Key': key,
                }
            ],
        },
    )


def detect_labels(photo_bucket, source_file):
    return client.detect_labels(Image={'S3Object': {'Bucket': photo_bucket, 'Name': source_file}}, MinConfidence=80)


# TODO get relevancy instead of taking max confidence
def get_best_label(label_array):
    max_confidence = 0
    best_label = ''
    people_tags = ('Person', 'Human', 'People')

    for item in label_array['Labels']:
        if item['Confidence'] >= max_confidence:
            best_label = item['Name']
            max_confidence = item['Confidence']

    return best_label


if __name__ == "__main__":
    bucket = 'pythonexercise1'#'aya-photos'
    #faceBucket = 'aya-saved-faces'
    sourceFile = 'test.jpg'

    '''pc = picamera.PiCamera()
    pc.capture('test.jpg')'''
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    while(True):
        cv2.imshow('img1',frame) #display the captured image
        if cv2.waitKey(1) & 0xFF == ord('y'): #save on pressing 'y'
            cv2.imwrite(sourceFile,frame)
            cv2.destroyAllWindows()
            break
    cap.release()

    upload_image(sourceFile, bucket)

    labelArray = detect_labels(bucket, sourceFile)

    bestLabel = get_best_label(labelArray)

    vowels = ('a', 'e', 'i', 'o', 'u')
    definiteArticle = ''
    if bestLabel[0].lower() in vowels:
        definiteArticle = 'an'
    else:
        definiteArticle = 'a'

    # Decide what to say here
    textToSpeak = "That is " + definiteArticle + " " + bestLabel.lower() + "!"
    print(textToSpeak)

    #delete_image(bucket, sourceFile)

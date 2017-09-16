import boto3
#import picamera
import numpy as np
import cv2
import time
import os
import json

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

def detect_faces(photo_bucket, source_file):
    return client.detect_faces(Image={'S3Object':{'Bucket':photo_bucket,'Name':source_file}},Attributes=['ALL'])

def detect_previous(photo_bucket, source_file, target_file):
    return client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':photo_bucket,'Name':source_file}},
                                  TargetImage={'S3Object':{'Bucket':photo_bucket,'Name':target_file}})

def play_mp3(fileName):
    os.system("mpg123 " + fileName)


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

def opencv_capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    while(True):
        cv2.imshow('img1',frame) #display the captured image
        if cv2.waitKey(1): #save on pressing 'y'
            cv2.imwrite(sourceFile,frame)
            cv2.destroyAllWindows()
            break
    cap.release()

def call_polly(text, fileName):
    start = "aws polly synthesize-speech \
    --output-format mp3 \
    --voice-id Joanna \
    --text '"
    end = "' \
    "
    os.system(start + text + end + fileName)

def article_message(labelArray):
    bestLabel = get_best_label(labelArray)
    vowels = ('a', 'e', 'i', 'o', 'u')
    definiteArticle = ''
    if len(bestLabel) >= 1:
        if bestLabel[0].lower() in vowels:
            definiteArticle = 'an'
        else:
            definiteArticle = 'a'
        # Decide what to say here
        textToSpeak = "That is " + definiteArticle + " " + bestLabel.lower() + "!"
    else:
        textToSpeak = "I have nothing to say."
    
    return textToSpeak

def message(text):
    fileName = "message.mp3"
    call_polly(text, fileName)
    play_mp3(fileName)

response = {
    'Person': "Oh hello, you look like a nice person.",
    'People': "Hello people.",
    'Human': "Looks like a nice human being.",
    'Bottle': "Oh you are so lucky, I wish I had that bottle. I am so thirsty . . .",
    'Mobile Phone': "Oh nice phone by the way."
    }

def analyze_labels(labelArray):
    enoughMessages = False
    personDone = False
    for label in labelArray['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
        if label['Name'] in response:
            message(response[label['Name']])
        else:
            message(article_message(labelArray))
        '''if (label['Name'] == 'Person' or label['Name'] == 'People') and not personDone:
            message("Oh hello, you look like a nice person.")
            personDone = True
            enoughMessages = True
        elif label['Name'] == 'Bottle':
            message("Oh you are so lucky, I wish I had that bottle. I am so thirsty . . .")
            enoughMessages = True
        elif label['Name'] == 'Mobile Phone':
            message("Oh nice phone by the way.")
            enoughMessages = True
        elif not enoughMessages:
            message(article_message(labelArray))
            break'''

def analyze_faces(faceArray):
    for faceDetail in faceArray['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))
        message("You look like someone between " + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + " years old")

def analyze_previous(previousArray, name):
    result = False
    for faceMatch in previousArray['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        confidence = str(faceMatch['Face']['Confidence'])
        print('The face at ' +
               str(position['Left']) + ' ' +
               str(position['Top']) +
               ' matches with ' + confidence + '% confidence')
        result = faceMatch['Face']['Confidence'] > 80
        if result:
            message("Hi " + name + ", nice seeing you back!")
    return result

def analyze_all_previous(sourceFile):
    previouslySeen = False
    targetFile = 'MathieuGodinSelfie.jpg'
    previousArray = detect_previous(bucket, sourceFile, targetFile)
    previouslySeen = analyze_previous(previousArray, "Mathieu")
    targetFile = 'balaji.jpg'
    previousArray = detect_previous(bucket, sourceFile, targetFile)
    previouslySeen = analyze_previous(previousArray, "Balaji")
    return previouslySeen

if __name__ == "__main__":
    play_mp3("intro.mp3")
    bucket = 'pythonexercise1'#'aya-photos'
    #faceBucket = 'aya-saved-faces'
    sourceFile = 'test.jpg'
    previouslySeen = False
    '''pc = picamera.PiCamera()
    pc.capture('test.jpg')'''
    count = 0
    while (count < 1):
        opencv_capture()
        upload_image(sourceFile, bucket)
        print("Comparing with previous faces . . .")
        previouslySeen = analyze_all_previous(sourceFile)
        if not previouslySeen:
            labelArray = detect_labels(bucket, sourceFile)
            faceArray = detect_faces(bucket, sourceFile)
            #print("Analyzing labels . . .")
            #analyze_labels(labelArray)
            print("Analyzing faces . . .")
            analyze_faces(faceArray)
        delete_image(bucket, sourceFile)
        count += 1
        #time.sleep(3)
    

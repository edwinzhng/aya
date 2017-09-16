import boto3
#import picamera
import numpy as np
import cv2
import time
import os

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

def analyze_image(labelArray):
    enoughMessages = False
    personDone = False
    for label in labelArray['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
        if (label['Name'] == 'Person' or label['Name'] == 'People') and not personDone:
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
            break
            

if __name__ == "__main__":
    play_mp3("intro.mp3")
    bucket = 'pythonexercise1'#'aya-photos'
    #faceBucket = 'aya-saved-faces'
    sourceFile = 'test.jpg'
    '''pc = picamera.PiCamera()
    pc.capture('test.jpg')'''
    count = 0
    while (count < 1):
        opencv_capture()
        upload_image(sourceFile, bucket)
        labelArray = detect_labels(bucket, sourceFile)
        print("Analyzing image . . .")
        analyze_image(labelArray)
        delete_image(bucket, sourceFile)
        count += 1
        time.sleep(3)
    

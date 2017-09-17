#!/usr/bin/python3
import picamera
import time
import os
import json

import s3
import aws
import facerecognition as fr

def play_mp3(fileName):
    os.system("mpg123-pulse " + fileName)

if __name__ == "__main__":
    collection = 'aya-faces'
    bucket = 'aya-photos'
    sourceFile = 'test.jpg'
    pc = picamera.PiCamera()

    play_mp3("audio/slience.mp3")
    play_mp3("audio/intro.mp3")

    count = 0
    while (count < 3):
        pc.capture(sourceFile)
        s3.upload_image(sourceFile, bucket)
        print("Checking collection for face...")
        existsPerson = aws.detect_faces(bucket, sourceFile)
        if existsPerson['FaceDetails']:
            foundFace = fr.searchFaces(collection, bucket, sourceFile)
            if foundFace['FaceMatches']:
                name = foundFace['FaceMatches'][0]['Face']['ExternalImageId']
                text = "Hi " + name + " nice to see you again!"
                print(text)
                aws.message(text)
            else:
                labelArray = aws.detect_labels(bucket, sourceFile)
                faceArray = aws.detect_faces(bucket, sourceFile)
                print("Analyzing labels...")
                aws.analyze_labels(labelArray)
                print("Analyzing faces...")
                aws.analyze_faces(faceArray)
        else:
            labelArray = aws.detect_labels(bucket, sourceFile)
            faceArray = aws.detect_faces(bucket, sourceFile)
            print("Analyzing labels...")
            aws.analyze_labels(labelArray)
            print("Analyzing faces...")
            aws.analyze_faces(faceArray)

        s3.delete_image(bucket, sourceFile)
        count += 1
        time.sleep(1)

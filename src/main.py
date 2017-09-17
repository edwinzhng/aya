#!/usr/bin/python3
import picamera
import time
import os
import json
import s3
import aws

def play_mp3(fileName):
    os.system("mpg123-pulse " + fileName)

if __name__ == "__main__":
    play_mp3("./audio/intro.mp3")
    bucket = 'aya-photos'
    sourceFile = 'test.jpg'
    previouslySeen = False
    pc = picamera.PiCamera()
    count = 0
    while (count < 1):
        pc.capture(sourceFile)
        s3.upload_image(sourceFile, bucket)
        print("Comparing with previous faces...")
        previouslySeen = aws.analyze_all_previous(bucket, sourceFile)
        if not previouslySeen:
            labelArray = aws.detect_labels(bucket, sourceFile)
            faceArray = aws.detect_faces(bucket, sourceFile)
            print("Analyzing labels...")
            aws.analyze_labels(labelArray)
            print("Analyzing faces...")
            aws.analyze_faces(faceArray)
        s3.delete_image(bucket, sourceFile)
        count += 1
        time.sleep(7)

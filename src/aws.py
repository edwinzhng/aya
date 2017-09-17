import boto3
import numpy as np # for openCV

def call_polly(text, fileName):
    start = "aws polly synthesize-speech \
    --output-format mp3 \
    --voice-id Joanna \
    --text '"
    end = "' \
    "
    os.system(start + text + end + fileName)

client = boto3.client('rekognition')

def detect_labels(photo_bucket, source_file):
    return client.detect_labels(Image={'S3Object': {'Bucket': photo_bucket, 'Name': source_file}}, MinConfidence=80)

def detect_faces(photo_bucket, source_file):
    return client.detect_faces(Image={'S3Object':{'Bucket':photo_bucket,'Name':source_file}},Attributes=['ALL'])

def detect_previous(photo_bucket, source_file, target_file):
    return client.compare_faces(SimilarityThreshold=70,
                                  SourceImage={'S3Object':{'Bucket':photo_bucket,'Name':source_file}},
                                  TargetImage={'S3Object':{'Bucket':photo_bucket,'Name':target_file}})

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

'''def opencv_capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    while(True):
        cv2.imshow('img1',frame) #display the captured image
        if cv2.waitKey(1): #save on pressing 'y'
            cv2.imwrite(sourceFile,frame)
            cv2.destroyAllWindows()
            break
    cap.release()
'''

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
    'People': "Hello everyone!",
    'Human': "Hey look, a nice human being.",
    'Bottle': "You are so lucky, I wish I had that bottle. I am so thirsty.",
    'Mobile Phone': "Hey that's a nice phone!"
    }

emotions = {
    'HAPPY40': "You seem happy.",
    'HAPPY60': "You look pretty happy.",
    'HAPPY80': "You look really happy!",
    'ANGRY40': "You don't look happy.",
    'ANGRY60': "Are you mad?",
    'ANGRY80': "What happened? You look pissed.",
    'CONFUSED40': "Do you have a question?",
    'CONFUSED60': "You look confused.",
    'CONFUSED80': "You look really confused.",
    'SAD40': "You look sad.",
    'SAD60': "You look a little bit sad.",
    'SAD80': "Are you crying?",
    'DISGUSTED40': "You look disgusted.",
    'DISGUSTED60': "You look a little bit disgusted.",
    'DISGUSTED80': "You look very disgusted. Do you dislike me?",
    'SURPRISED40': "You look surprised.",
    'SURPRISED60': "You look really surprised.",
    'SURPRISED80': "Are you surprised that I can communicate with you?",
    'CALM40': "You look calm.",
    'CALM60': "You look really calm.",
    'CALM80': "You look so calm. I like that. I like calm people."
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
            message("You are so lucky, I wish I had that bottle. I am so thirsty.")
            enoughMessages = True
        elif label['Name'] == 'Mobile Phone':
            message("Hey that's a nice phone!")
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
        for emotion in faceDetail['Emotions']:
            emotionString = emotion['Type'] + str(int(emotion['Confidence'] // 20 * 20))
            if emotionString in emotions:
                message(emotions[emotionString])

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
            message("Hi " + name + ", nice to see you again!")
    return result

def analyze_all_previous(bucket, sourceFile):
    previouslySeen = False
    targetFile = 'MathieuGodinSelfie.jpg'
    previousArray = detect_previous(bucket, sourceFile, targetFile)
    previouslySeen = analyze_previous(previousArray, "Mathieu")
    targetFile = 'balaji.jpg'
    previousArray = detect_previous(bucket, sourceFile, targetFile)
    previouslySeen = analyze_previous(previousArray, "Balaji")
    return previouslySeen

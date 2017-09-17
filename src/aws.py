import boto3
import os
from playsound import playsound

client = boto3.client('rekognition')

def call_polly(text, fileName):
    start = "aws polly synthesize-speech \
    --output-format ogg_vorbis \
    --voice-id Joanna \
    --text '"
    end = "' \
    "
    os.system(start + text + end + fileName)

def detect_labels(photo_bucket, source_file):
    return client.detect_labels(Image={'S3Object': {'Bucket': photo_bucket, 'Name': source_file}}, MinConfidence=80)

def detect_faces(photo_bucket, source_file):
    return client.detect_faces(Image={'S3Object':{'Bucket':photo_bucket,'Name':source_file}},Attributes=['ALL'])

def get_best_label(label_array):
    max_confidence = 0
    best_label = ''
    people_tags = ('Person', 'Human', 'People')

    for item in label_array['Labels']:
        if item['Confidence'] >= max_confidence:
            best_label = item['Name']
            max_confidence = item['Confidence']

    return best_label

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
    fileName = "message.ogg"
    call_polly(text, fileName)
    playsound(fileName) # play sound

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
        if faceDetail['Beard']['Value'] == True:
            message("Nice beard!")
        if faceDetail['Eyeglasses']['Value'] == True:
            message("I really like your glasses. You look sexy with that.")
        if faceDetail['EyesOpen']['Value'] == False:
            message("Your eyes are closed, are you sleeping?")
        if faceDetail['MouthOpen']['Value'] == True:
            message("Keep your mouth shut!")
        if faceDetail['Mustache']['Value'] == True:
            message("Nice mustache!")
        if faceDetail['Smile']['Value'] == True:
            message("I like your smile.")
        if faceDetail['Sunglasses']['Value'] == True:
            message("Nice sunglasses!")
        if "Male" in faceDetail['Gender'] and faceDetail['Gender']['Confidence'] > 99.9:
            message("You really look male.")
        if "Female" in faceDetail['Gender'] and faceDetail['Gender']['Confidence'] > 99.9:
            message("You really look feminine.")

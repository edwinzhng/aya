import boto3

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
    return client.detect_labels(Image={'S3Object': {'Bucket': photo_bucket, 'Name': source_file}},
                                        MinConfidence=80)


# TODO get relevancy instead of taking max confidence
def get_best_label(label_array, exists_person):
    max_confidence = 0
    best_label = ''
    people_tags = ('Person', 'Human', 'People')

    for item in label_array['Labels']:
        if (item['Name'] in people_tags) & (not exists_person):
            exists_person = True
            print('Found a person!')
        if item['Confidence'] >= max_confidence:
            best_label = item['Name']
            max_confidence = item['Confidence']

    return best_label


if __name__ == "__main__":
    bucket = 'aya-photos'
    faceBucket = 'aya-saved-faces'
    sourceFile = 'test.jpg'

    upload_image(sourceFile, bucket)

    labelArray = detect_labels(bucket, sourceFile)

    existsPerson = False
    bestLabel = get_best_label(labelArray, existsPerson)


    vowels = ('a', 'e', 'i', 'o', 'u')
    definiteArticle = ''
    if bestLabel[0].lower() in vowels:
        definiteArticle = 'an'
    else:
        definiteArticle = 'a'

    # Decide what to say here
    textToSpeak = "That is " + definiteArticle + " " + bestLabel.lower() + "!"
    print(textToSpeak)

    # Iterate through names
    currentName = 'edwin'
    targetFile = currentName + '.jpg'

    # Compare faces
    if existsPerson:
        compareResponse = client.compare_faces(SimilarityThreshold=70,
                                        SourceImage={'S3Object': {'Bucket': bucket, 'Name': sourceFile}},
                                        TargetImage={'S3Object': {'Bucket': bucket, 'Name': targetFile}})
        if compareResponse['FaceMatches']['Face']['Confidence'] > 90:
            print("Hello, " + currentName + ". Nice to see you again!")

    delete_image(bucket, sourceKey)
import boto3

client = boto3.client('rekognition')

def addFaceToCollection(collection, bucket, sourceImage, savedName){
response = client.index_faces(
    CollectionId='aya-faces',
    Image={
        'S3Object': {
            'Bucket': bucket,
            'Name': sourceImage,
        }
    },
    ExternalImageId=savedName,
    )
}


def searchFaces(collection, bucket, sourceImage){
    response = client.search_faces_by_image(
        CollectionId=collection,
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': sourceImage,
            }
        },
    )
    return response['FaceMatches']['Face']['FaceId']
}

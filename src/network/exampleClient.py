# An example of how piboard will call api
import requests
import time
import os

# Get Environment Variables
from network.exampleClientVariables import kiosk_id, request_url, imagesLocation

def getRequest():
    # simple get response to check if api is working
    return requests.get(f"{request_url}/")

def postRequest():
    sendTime = time.time() # get pre send time stamp
    images = imagesToSend() # get all the images that need to be sent
    fullURL = f"{request_url}/eye_evaluation/{kiosk_id}" # create the full URL
    response = requests.post(fullURL, files=images)
    return response

def imagesToSend():
    # Gets all the images that need to be sent in the post request
    images = os.listdir(imagesLocation) # use location of current sessions images
    files = []
    for image in images:
        files.append(('images', (image, open(f'{imagesLocation}/{image}', 'rb'), 'image/jpeg')))
    return files


def backendRequests(requestType):
    # specify which request is being made
    if requestType == "get":
        return  getRequest()
    if requestType == "post":
        return  postRequest()


# For testing
def main():
    response = backendRequests("post")
    status = response.status_code
    if status == 200:
        info = response.json()
        print(info)
    else :
        print(status)

if __name__ == '__main__':
    main()

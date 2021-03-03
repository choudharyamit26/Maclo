# import urllib.request
#
# x=urllib.request.urlretrieve("https://graph.facebook.com/1353570358316412/picture?type=normal", "local-filename.jpg")
# print(x)
# print(type(x))
# print('after image download')


import requests
import os
image_url = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
img_data = requests.get(image_url).content
print(img_data)
with open('image_name2.png', 'wb') as handler:
    handler.write(img_data)
    print(handler.name)
    print(os.path.abspath(handler.name))
os.remove('image_name1.png')

# import urllib
# resource = urllib.urlopen("http://www.digimouth.com/news/media/2011/09/google-logo.jpg")
# output = open("file01.jpg","wb")
# output.write(resource.read())
# output.close()
# MIT License
#
# Copyright (c) 2018 Peshmerge Morad
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import os
import re
import requests
from PIL import Image, ImageDraw, ImageFont

# The Check/Recognize API which can be used to send an image to machineboxx/facebox.
check_api_url = "http://localhost:8080/facebox/check"

# Health API url as defined by MachineBox to fetch the status/health of the box
health_api_url = "http://localhost:8080/readyz"


def main(args):
    try:
        json_response = requests.get(health_api_url)
    except requests.exceptions.RequestException as e:
        print("Facebox is unreachable......... Please check if it's up and running! ")
        print(e)
    else:
        if json_response.status_code == 200:
            with open(args["image"], "rb") as image_file:
                json_response = (requests.post(
                    check_api_url,
                    files={'file': open(args["image"], 'rb')}
                )).json()
                im = Image.open(image_file)
                draw = ImageDraw.Draw(im)
                if json_response["success"] == True:
                    for face in (json_response["faces"]):
                        height = face["rect"]["height"]
                        left = face["rect"]["left"]
                        top = face["rect"]["top"]
                        width = face["rect"]["width"]
                        box = [(left, top),
                               (left + width, top),
                               (left + width, top + height),
                               (left, top + height),
                               (left, top)]
                        draw.line(box, width=1, fill='#00ff00')
                        font = ImageFont.truetype('Roboto-Bold.ttf', size=15)
                        color = 'rgb(255, 0, 0)'  # black color
                        face_label = "Unknown" if face["matched"] == False else str(face["name"]) + " "+str(
                            round(float(face["confidence"]), 2))
                        draw.text((left, top - 20),
                                  text=face_label,
                                  fill=color,
                                  font=font)
                    im.show()
                file_name = (re.sub('[.]', '', os.path.splitext(args["image"])[0])).strip('\\')
                if args["save"] == 'yes':
                    im.save('machinebox-' + file_name + '.jpg')
        else:
            print("The Machinebox/Facebox isn't ready! Please check if the docker instance is up an running!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Image recognition Service"
    )
    parser.add_argument('-i', '--image')
    parser.add_argument('-s', '--save')
    args = vars(parser.parse_args())
    main(args)

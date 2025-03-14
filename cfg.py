#!/usr/bin/env python3
"""
I use this file to act as a shared area for functions as well as shared global variables.
"""

import requests

def init():
    global apiendpoint
    global instanceurl
    global api1instance
    global abouturl
    global themeArr
    global itemArr
    global jaVersion


# Be sure to create a creds.py file in this same directory, defining jatoken and username
# See readme for more details.

#_______________________________________________________________________________

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        #print("Token: " + self.token)
        return r
#_______________________________________________________________________________
# When you pull a work item from the API, sometimes users put commas in the text fields
# I use this to replace the commas with dashes when I call it in JAviaAPI2
def ReplaceStrings(txt,remove,replace):
    if txt and "," in txt:
        txt = txt.replace(remove,replace)
        return txt
    else:
        return txt
#_______________________________________________________________________________
# When you use the csv writer, it is sometimes insertings carriage returns or line feeds when it finds
# them in a field. I use the below to strip those out so I get all of the values written into one
# continuous line. Preserving this makes it easy to then take this file and use it for an import
def RemoveEOLChar(txteol):
    if txteol:
        #print(txteol)
        txteol = txteol.replace('\r','')
        txteol = txteol.replace('\n','')
        #print(txteol)
    return txteol
#_______________________________________________________________________________


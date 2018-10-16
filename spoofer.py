# ==========================================
#  File Name: spoofer.py
#  Title: Find My Friends & Find My iPhone Spoofer
#  Description: python command line script to spoof FindMyFriends
#  Author: AT-TAI
# ==========================================

# Libraries
import urllib
import urllib2
import getpass
import sys
import base64
import plistlib
import traceback
import json
import time

# find device
def getUDID(dsid, mmeFMFAppToken):
    url = 'https://p04-fmfmobile.icloud.com/fmipservice/friends/%s/1/maxCallback/refreshClient' % dsid
    headers = {
        'Authorization': 'Basic %s' % base64.b64encode("%s:%s" % (dsid, mmeFMFAppToken)), # FMF APP TOKEN
        'Content-Type': 'application/json; charset=utf-8',
    }
    data = {
        "clientContext": {
            "appVersion": "5.0" # for getting config/time
        }
    }
    jsonData = json.dumps(data)
    request = urllib2.Request(url, jsonData, headers)
    i = 0
    while 1:
        try:
            response = urllib2.urlopen(request)
            break
        except:
            i +=1
            continue
    x = json.loads(response.read())
    try:
        UDID = base64.b64decode(x["devices"][0]["id"].replace("~", "="))
    except Exception, e:
        # if this throws an error, allow manual UDID input
        UDID = (False, False)
    return (UDID, x["devices"][0]["name"])

# 2FA still work in progress

def tokenFactory(dsid, mmeAuthToken):
    mmeAuthTokenEncoded = base64.b64encode("%s:%s" % (dsid, mmeAuthToken))
    url = "https://setup.icloud.com/setup/get_account_settings"
    headers = {
        'Authorization': 'Basic %s' % mmeAuthTokenEncoded,
        'Content-Type': 'application/xml',
        'X-MMe-Client-Info': '<iPhone6,1> <iPhone OS;9.3.2;13F69> <com.apple.AppleAccount/1.0 (com.apple.Preferences/1.0)>'
    }
    request = urllib2.Request(url, None, headers)
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            return "HTTP Error: %s" % e.code
        else:
            print e
            raise HTTPError
    content = response.read()
    mmeFMFAppToken = plistlib.readPlistFromString(content)["tokens"]["mmeFMFAppToken"]
    mmeFMIToken = plistlib.readPlistFromString(content)["tokens"]["mmeFMIPToken"]
    return (mmeFMFAppToken, mmeFMIToken)

####################################

def dsidFactory(uname, passwd):
    creds = base64.b64encode("%s:%s" % (uname, passwd))
    url = "https://setup.icloud.com/setup/authenticate/%s" % uname
    headers = {
        'Authorization': 'Basic %s' % creds,
        'Content-Type': 'application/xml',
    }
    request = urllib2.Request(url, None, headers)
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            if e.code == 401:
                return "HTTP Error Unauthorized! Check creds?"
            elif e.code == 409:
                return "HTTP Error Conflict! 2 Factor Authentication appears to be enabled."
            elif e.code == 404:
                return "HTTP Error URL not found! Username error?"
            else:
                return "HTTP Error %s.\n" % e.code
        else:
            print e
            raise HTTPError
    content = response.read()
    DSID = int(plistlib.readPlistFromString(content)["appleAccountInfo"]["dsPrsID"])
    mmeAuthToken = plistlib.readPlistFromString(content)["tokens"]["mmeAuthToken"]
    return (DSID, mmeAuthToken)

def convertAddress(street, city, state):
    street = street.replace(" ", "+")
    city = city.replace(" ", "+")
    url = "http://maps.google.com/maps/api/geocode/json?address=%s,+%s+%s" % (street, city, state)
    headers = {
        'Content-Type': 'application/json',
    }
    request = urllib2.Request(url, None, headers)
    response = None
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            return "HTTP Error: %s" % e.code
        else:
            print e
            raise HTTPError
    coords = json.loads(response.read())["results"][0]["geometry"]["location"]
    return (coords["lat"], coords["lng"])

def fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude):
    mmeFMITokenEncoded = base64.b64encode("%s:%s" % (DSID, mmeFMIToken))
    url = 'https://p04-fmip.icloud.com/fmipservice/findme/%s/%s/currentLocation' % (DSID, UDID)
    headers = {
        'Authorization': 'Basic %s' % mmeFMITokenEncoded,
        'X-Apple-PrsId': '%s' % DSID,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Accept-Language': 'en-us',
        'User-Agent': 'FMDClient/6.0 iPhone6,1/13F69',
        'X-Apple-Find-API-Ver': '6.0',
    }
    data = {
        "locationFinished": False,
        "deviceInfo": {
            "batteryStatus": "NotCharging",
            "udid": UDID,
            "batteryLevel": 0.50,
            "isChargerConnected": False
        },
        "longitude": longitude,
        "reason": 1,
        "horizontalAccuracy": 65,
        "latitude": latitude,
        "deviceContext": {
        },
    }
    jsonData = json.dumps(data)
    request = urllib2.Request(url, jsonData, headers)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            return "Error changing FindMyiPhone location, status code <%s>!" % e.code
        else:
            print e
            raise HTTPError
    return "Successfully changed FindMyiPhone location to <%s,%s>!" % (latitude, longitude)

def fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude):
    mmeFMFAppTokenEncoded = base64.b64encode("%s:%s" % (DSID, mmeFMFAppToken))
    url = 'https://p04-fmfmobile.icloud.com/fmipservice/friends/%s/%s/myLocationChanged' % (DSID, UDID)
    headers = {
        'host': 'p04-fmfmobile.icloud.com',
        'Authorization': 'Basic %s' % mmeFMFAppTokenEncoded,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'User-Agent': 'FindMyFriends/5.0 iPhone6,1/9.3.2(13F69)',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us',
        'X-Apple-Find-API-Ver': '2.0',
        'X-Apple-AuthScheme': 'Forever',
    }
    data = {
        "serverContext": {
            "authToken": "%s" % mmeFMFAppToken,
            "prsId": DSID,
        },
        "clientContext": {
            "appName": "FindMyFriends",
            "appVersion": "5.0",
            "userInactivityTimeInMS": 5,
            "deviceUDID": "%s" % UDID,
            "location": {
                "altitude": 57,
                "longitude": "%s" % longitude,
                "source": "app",
                "horizontalAccuracy": 1.0,
                "latitude": "%s" % latitude,
                "speed": -1,
                "verticalAccuracy": 1.0
            }
        }
    }
    jsonData = json.dumps(data)
    request = urllib2.Request(url, jsonData, headers)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        if e.code != 200:
            return "Error changing FindMyFriends location, status code <%s>!" % e.code
        else:
            print e
            raise HTTPError
    return "Successfully changed FindMyFriends location to <%s,%s>!" % (latitude, longitude)

if __name__ == '__main__':
    user = raw_input("Apple ID: ")
    try:
        int(user)
        user = int(user)
    except ValueError:
        pass
    passw = getpass.getpass()
    try:
        (DSID, authToken) = dsidFactory(user, passw)
        print "Got DSID/MMeAuthToken [%s:%s]!" % (DSID, authToken)
        print "Successfully authenticated to iCloud!"
    except:
        print "Error getting DSID and MMeAuthToken!\n%s" % dsidFactory(user, passw)
        sys.exit()
    while True:
        try:
            arg = float(raw_input("Would you like to use GPS coordinates [1] or a street address [2]: "))
            if not (1 <= arg <= 2):
                raise ValueError()
            break
        except ValueError:
            print "Please enter 1 or 2 (GPS coordinates, or street address)"
            continue
    latitude, longitude, street, city, state = (None, None, None, None, None)
    if arg == 1.0:
        latitude = raw_input("Latitude: ")
        longitude = raw_input("Longitude: ")
    if arg == 2.0:
        street = raw_input("Street address: ")
        city = raw_input("City: ")
        state = raw_input("State: ")
        (latitude, longitude) = convertAddress(street, city, state)
        print "Got GPS coordinates <%s:%s> for %s, %s, %s" % (latitude, longitude, street, city, state)

    while True:
        try:
            serviceSelect = int(raw_input("Spoof FMF, FMI, or both: [0, 1, 2] "))
            if not (0 <= serviceSelect <= 2):
                raise ValueError()
            break
        except ValueError:
            print "Please enter 0, 1 or 2 (FMF, FMI, or both, respectively)"
            continue

    try:
        mmeFMFAppToken, mmeFMIToken = tokenFactory(DSID, authToken)
    except Exception as e:
        print "Error getting FMF/FMI tokens!\n%s" % e
        traceback.print_exc()
        sys.exit()
    print "Attempting to find UDID's for devices on account."
    UDID = getUDID(DSID, mmeFMFAppToken)
    if UDID[0] != False:
        print "Found UDID [%s] for device [%s]!" % (UDID[0], UDID[1])
        confirm = raw_input("Do you want to spoof this device? [y/n] ")
        confirm = "n"
        if confirm == "y" or confirm == "Y" or confirm == "yes" or confirm == "Yes":
            UDID = UDID[0]
        else:
            UDID = raw_input("Okay, enter UDID manually: ")
    else:
        print "Could not get UDID for any device"
        UDID = raw_input("UDID: ")
    try:
        while True:
            if serviceSelect == 0 or serviceSelect == 1 or serviceSelect == 2:
                if serviceSelect == 0:
                    print fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude)
                    print "Waiting 1 second to send FMF spoof again."
                    time.sleep(1)
                elif serviceSelect == 1:
                    print fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude)
                    print "Waiting 1 second to send FMI spoof again."
                    time.sleep(1)
                else:
                    print fmiSetLoc(DSID, mmeFMIToken, UDID, latitude, longitude)
                    print fmfSetLoc(DSID, mmeFMFAppToken, UDID, latitude, longitude)
                    print "Waiting 1 second to send FMI/FMF spoof again."
                    time.sleep(1)
            else:
                print "Service select must have a value of 0, 1, or 2."
                sys.exit()
    except KeyboardInterrupt:
        print "Terminated. Stopping spoof."
        print "Spoofing stopped."
    except Exception as e:
        print e
        print traceback.print_exc()
        sys.exit()

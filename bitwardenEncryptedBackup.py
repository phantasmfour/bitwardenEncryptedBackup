'''
Bitwarden Encrypted Backup
When you authenticate to Bitwarden you get all your credentials back in an encrypted form.
This is like when you use the use the bitwarden desktop app and you get back a data.json
You can do this with only preAuthentication using API keys and set this up as a backup script via a daily cron. Bascially all unauthenticated data until you put in your master key.

Using BitwardenDecrypt from Gurpeet here you can decrypt this later with your master password https://github.com/GurpreetKang/BitwardenDecrypt
If you are ever in the situation where you lost your data you can at least still have your creds and are able to import the json file you get back from Gurpeets script to import back into Bitwarden

Phantasm 03/2023
'''


import requests  # Interact with Bitwarden API
import json  # Write file
from datetime import date  # For file name

API_CLIENT_ID = "**********"  # Enter Yours Here 
API_CLIENT_SECRET = "*************"  # Enter Yours Here
bitwarden_url = "https://*******"  # Enter Yours Here


postHeaders = {'User-Agent':'Bitwarden_Backup','Connection':'close'}  # Fun user agent just incase you have traffic logs. and Kill the connection after the request is done since thats how the cli does it.
postPayload = {'scope':'api','client_id':API_CLIENT_ID,'deviceType':'8','deviceIdentifier':'identify-me','deviceName':'bitwarden backup','grant_type':'client_credentials','client_secret':API_CLIENT_SECRET}  # All this is needed, you can put junk for most of the values like I did, still works.

bitwardenSession = requests.Session()  # Probably don't need a session but incase we expand later
bitPostResponse = bitwardenSession.post(bitwarden_url + "/identity/connect/token",headers=postHeaders,data=postPayload,verify=False)  # Need data rather than json since thats how the request wants it. Verify to ignore self signed
jsonResponse = bitPostResponse.json()
authKey = jsonResponse["access_token"]  # Everything else is mostly junk for what we are doing but you can save off your kdf settings if you want.

getHeaders = {'User-Agent':'Bitwarden_Backup','Connection':'close','Authorization': 'Bearer {}'.format(authKey)}
bitGetResponse = bitwardenSession.get(bitwarden_url + "/api/sync?excludeDomains=true",headers=getHeaders,verify=False)  # Syncs and pulls down all your encrypted data. Can remove verify if you have ssl certificate
backupData = bitGetResponse.json()


# formatting Creds how they look in data.json
credDict = {}
for item in backupData['ciphers']:
    credDict[item['id']] = {
        "id": item['id'],
        "organizationId": item['organizationId'],
        "folderId": item['folderId'],
        "edit": item['edit'],
        "viewPassword": item['viewPassword'],
        "organizationUseTotp": item['organizationUseTotp'],
        "favorite": item['favorite'],
        "revisionDate": item['revisionDate'],
        "type": item['type'],
        "name": item['name'],
        "notes": item['notes'],
        "collectionIds": item['collectionIds'],
        "deletedDate": item['deletedDate'],
        "reprompt": item['reprompt'],
        "login": item['login']
    }

# Does not really need to happen given folders are kind of unimportant without a way to put this data back in but will do anyways + plus don't want to recode other persons library to fit my format. Formatting folders
folderDict = {}
for item in backupData['folders']:
    folderDict[item['id']] = {
        "name": item['name'],
        "id": item['id'],
        "revisionDate": item['revisionDate']
    }

# Formatting this similar to how data.json should look.
formatedOutput = {
  "global": {
    "theme": "system",
    "window": {},
    "stateVersion": 6,
    "environmentUrls": {
      "base": "not needed",
      "api": "nothing",
      "identity": "nothing",
      "webVault": "nothing",
      "icons": "nothing",
      "notifications": "nothing",
      "events": "nothing",
      "keyConnector": "nothing"
    },
    "installedVersion": "not relevant"
  },
  "authenticatedAccounts": [
    backupData['profile']['id']
  ],
  "appId": "not Needed",
  backupData['profile']['id']: {
    "data": {
      "ciphers": {
        "encrypted": credDict
      },
      "folders": {
        "encrypted": folderDict
      },
      "sends": {
        "encrypted": {}
      },
      "collections": {
        "encrypted": {}
      },
      "policies": {
        "encrypted": {}
      },
      "passwordGenerationHistory": {},
      "organizations": {},
      "providers": {},
    },
    "keys": {
      "cryptoSymmetricKey": {
        "encrypted": backupData['profile']['key']
      },
      "organizationKeys": {
        "encrypted": {}
      },
      "providerKeys": {
        "encrypted": {}
      },
      "privateKey": {
        "encrypted": backupData['profile']['privateKey']
      },
      "apiKeyClientSecret": API_CLIENT_SECRET
    },
    "profile": {
        "userId": backupData['profile']['id'],
        "name": backupData['profile']['name'],
        "email": backupData['profile']['email'],
        "hasPremiumPersonally": False,
        "kdfIterations": jsonResponse['KdfIterations'],
        "kdfType": jsonResponse['Kdf'],
        "apiKeyClientId": API_CLIENT_ID,
        "emailVerified": False,
        "usesKeyConnector": False,
        "convertAccountToKeyConnector": "nothing",
        "lastSync": "2005-02-11T25:03:21.874Z"

    },
    "settings": {
      "environmentUrls": {
        "base": "not needed",
        "api": "nothing",
        "identity": "nothing",
        "webVault": "nothing",
        "icons": "nothing",
        "notifications": "nothing",
        "events": "nothing",
        "keyConnector": "nothing"
      },
      "pinProtected": {
        "encrypted": "nothing",
        "decrypted": "nothing"
      },
      "protectedPin": "nothing",
      "settings": {
        "equivalentDomains": []
      },
      "vaultTimeoutAction": "lock"
    },
    "tokens": {
      "accessToken": "not needed"
    }
  },
  "accountActivity": {
    "not needed": 2312
  },
  "activeUserId": "not needed"
}
# Can compare this to a data.json file to see what I was going for since this file can be easily imported into Gurpeets script

# No file rotation, bitwarden has password history and trash recovery so I am not using this as a deleted password recovery, more of if the server goes down
json_output = json.dumps(formatedOutput,indent=4)  # Write to file
fileName =  "bitwardenBackup_{}.json".format(date.today())  # Can put your own filename here
with open(fileName,"w") as outfile:  # always overwrite the file
    outfile.write(json_output)

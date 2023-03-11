'''
Bitwarden Encrypted Backup
When you authenticate to Bitwarden you get all your credentials back in an encrypted form.
If you find a way to decrypt this using your master key later this will work
I did not dig into that enough but this is a good starting place https://www.huy.rocks/everyday/02-22-2022-security-how-bitwarden-encrypts-your-data

Right now this just returns encrypted data. You cannot import it back since we need to derive the encKeyValidation
Not worth time right now.
Phantasm 03/2023
'''


import requests  # Interact with Bitwarden API
import json  # Write file
API_CLIENT_ID = "********"
API_CLIENT_SECRET = "***********"


bitwarden_url = "https://bitwarden"
postHeaders = {'User-Agent':'Bitwarden_Backup','Connection':'close'}  # Fun user agent just incase you have traffic logs. and Kill the connection after the request is done since thats how the cli does it.
postPayload = {'scope':'api','client_id':API_CLIENT_ID,'deviceType':'8','deviceIdentifier':'identify-me','deviceName':'bitwarden backup','grant_type':'client_credentials','client_secret':API_CLIENT_SECRET}  # All this is needed, you can put junk for most of the values like I did, still works.

bitwardenSession = requests.Session()  # Probably don't need a session but incase we expand later
bitPostResponse = bitwardenSession.post(bitwarden_url + "/identity/connect/token",headers=postHeaders,data=postPayload,verify=False)  # Need data rather than json since thats how the request wants it. Verify to ignore self signed
jsonResponse = bitPostResponse.json()
authKey = jsonResponse["access_token"]  # Everything else is junk for what we are doing but you can save off your kdf settings if you want.

getHeaders = {'User-Agent':'Bitwarden_Backup','Connection':'close','Authorization': 'Bearer {}'.format(authKey)}
bitGetResponse = bitwardenSession.get(bitwarden_url + "/api/sync?excludeDomains=true",headers=getHeaders,verify=False)  # Syncs and pulls down all your encrypted data
backupData = bitGetResponse.json()

# Formatting this similar to how you export the data via the gui this is what it looks like.
formatedOutput = {
    "encrypted":True,
    "encKeyValidation_DO_NOT_EDIT":backupData['profile']['key'],  # THIS IS WRONG AND IS THE "KEY"
    "folders":backupData['folders'],
    "items":backupData['ciphers']
}

json_output = json.dumps(formatedOutput,indent=4)  # Write to file
with open("bitwardenBackup.json","w") as outfile:
    outfile.write(json_output)

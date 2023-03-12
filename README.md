# Bitwarden Encrypted Backup Via API

Using this script you are able to Authenticate to Bitwarden via the API.

You are not fully authenticated to decrypt secrets until you provide the master password. 

But you are given a file similar to clients called data.json. 

The formatting is different but you are able to take this file which contains your encrypted credentials and send it to BitwardenDecrypt

---

This script [BitwardenDecrypt](https://github.com/GurpreetKang/BitwardenDecrypt) by Gurpeet does most of the actual work. They wrote this to decrypt data.json file. 

With my script I am jsut pulling down the crednetials and then formatting them into a data.json like file.

You can run this as a cron script and later if you need these password just decrypt them. And if that is not enough the output you get from Gurpeets script can be imported back into bitwarden to reimport your password.

I imagine this script running in cron daily overwritting the save file.
Only issues to watch out for is if you change your API Creds. I do not have any error handling so you might not know.


Example:
`python3 bitwardenEncryptedBackup.py`

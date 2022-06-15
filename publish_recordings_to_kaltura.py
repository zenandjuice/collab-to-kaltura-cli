import requests, json, datetime, jwt, re
from urllib.parse import urlencode
from KalturaClient import *
from KalturaClient.Plugins.Core import *

def main():
    oAuth = get_token()
    kaltura = get_kaltura_client()

    recording_list = open('publish_recordings_to_kaltura.txt', 'r')

    for recording in recording_list:
        recording_uuid, course_id, owner = recording.split("\t")
        get_recordings(recording_uuid, course_id, owner, oAuth, kaltura)

    recording_list.close()

def get_recordings(recording_uuid, course_id, owner, oAuth, kaltura):

    rest = requests.get(oAuth["endpoint"]+"/recordings/"+recording_uuid,
        headers={"Authorization":"Bearer "+oAuth["token"],
                 "Content-Type":"application/json"
                 }
        )

    if rest.text:
        recording = json.loads(rest.text)

        if recording["publicLinkAllowed"] ==False:
            print("Not Public: "+recording["name"])

        else:
            start_date = datetime.datetime.strptime(recording["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            recording_name = re.sub(r'[^a-zA-Z0-9\_\-\s\"\']', '', recording["name"])
            get_recording_data(recording["id"], course_id, course_id+" "+recording_name+" - "+start_date.strftime("%m/%d/%Y"), owner, oAuth, kaltura)


def get_recording_data(recording_uuid, course_id, recording_name, owner, oAuth, kaltura):

    rest = requests.get(oAuth["endpoint"]+"/recordings/"+recording_uuid+"/data",
        headers={"Authorization":"Bearer "+oAuth["token"],
                 "Content-Type":"application/json"
                 }
        )

    if rest.status_code == 401:
        oAuth = get_token()
        get_recording_data(recording_uuid, course_id, recording_name, owner, oAuth, kaltura)

    elif rest.text:
        response = json.loads(rest.text)
        if "extStreams" in response:
            if "streamUrl" in response["extStreams"][0]:
                download_url = response["extStreams"][0]["streamUrl"]
                tags = "collaborate_recording,"+course_id
                kaltura_file_upload(kaltura, download_url, recording_name, recording_uuid, tags, owner)

            else:
                print("Stream URL not found: "+recording_name)

        else:
            print("External Stream not found: "+recording_name+" "+response)


def kaltura_file_upload(client, url, name, recording_uuid, tags, owner_id):
    entry = KalturaMediaEntry()
    entry.mediaType = KalturaMediaType.VIDEO
    entry.name = name
    entry.description = "Collaborate Recording ID:"+recording_uuid
    entry.tags = tags
    entry.userId = owner_id
    entry.referenceId = "Collaborate_"+recording_uuid
    mediaEntry = client.media.add(entry)
    entryId = mediaEntry.id

    resource = KalturaUrlResource()
    resource.url = url
    result = client.media.addContent(entryId, resource)

    print("Success: "+recording_uuid+" "+name+" "+mediaEntry.id)


def get_token():
    oAuth = {
        "key" : "[collab_lti_key]",
        "secret" : "[collab_lti_secret]",
        "endpoint" : "https://us.bbcollab.com/collab/api/csa"
    }

    grant_type = "urn:ietf:params:oauth:grant-type:jwt-bearer"

    exp = datetime.datetime.utcnow() + datetime.timedelta(minutes = 120)

    claims = {
        "iss" : oAuth["key"] ,
        "sub" : oAuth["key"] ,
        "exp" : exp
    }

    assertion = jwt.encode(claims, oAuth["secret"], "HS256")

    payload = {
        "grant_type": grant_type,
        "assertion" : assertion
    }

    rest = requests.post(
        oAuth["endpoint"]+"/token",
        data = payload,
        auth = (oAuth["key"], oAuth["secret"])
        )

    #print("[auth:setToken()] STATUS CODE: " + str(rest.status_code) )

    res = json.loads(rest.text)
    #print("[auth:setToken()] RESPONSE: \n" + json.dumps(res,indent=4, separators=(",", ": ")))

    if rest.status_code == 200:
        parsed_json = json.loads(rest.text)
        oAuth["token"] = parsed_json['access_token']
        oAuth["token_expires"] = parsed_json['expires_in']

    else:
        print("[auth:setToken()] ERROR: " + str(rest))


    return oAuth

def get_kaltura_client():
    config = KalturaConfiguration([kaltura_partner_id])
    config.serviceUrl = "https://admin.kaltura.com/"
    client = KalturaClient(config)
    get_kaltura_token(client)

    return client



def get_kaltura_token(client):

    ks = client.session.start(
         "[kaltura_admin_secret]",
         None,
         KalturaSessionType.ADMIN,
         [kaltura_partner_id],
         432000,
         "disableentitlement"
         )

    client.setKs(ks)

main()

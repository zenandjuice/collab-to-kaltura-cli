# Publish Collaborate to Kaltura command line tool

This code was originally written by Heather Crites (https://github.com/hcrites-cscc) and requires the Kaltura Client for Python (https://pypi.org/project/KalturaApiClient/).

Launch with:

    python3 publish_recordings_to_kaltura.py

This script looks for a "publish_recordings_to_kaltura.txt" file in the same folder.  This file contains 3 fields in a tab delmiited format:

collab_recording_id bb_course_id username

example:
1a3d015ddac62cf14cec249a939af4a7  1223-SUBJ-1234  chris

and then using Collaborate and Kaltura REST, it publishes the recordings into Kaltura with the following details:

Entry Name:  _course_id_ _recording full_name_ - _recording_date_
Tags: "collaborate_recording" & _course_id_
ReferenceID: Collaborate__recording_id_
Owner: _username_

Example:

Entry Name: 1223-SUBJ-1234 Session 35 - Nov 13 - recording_1 - 11/13/2020
Tags: "collaborate_recording", "1223-SUBJ-1234"
ReferenceID: "Collaborate_1a3d015ddac62cf14cec249a939af4a7"
Owner: chris

To use, you will need your Collaborate LTI Key and Secret and Kaltura Partner ID and admin secret.

This only works with PUBLIC Collaborate Ultra recordings.  If your recordings are not public, open a Blackboard support ticket and they can change the visibility of recordings.


Edit:

Line 84 - Collab LTI key (Consumer Key in Collaborate Ultra Building Block)

Line 85 - Collab LTI secret (Shared Secret in Collaborate Ultra Building Block)

Line 86 - Collab CSA Service URL

Line 129: Kaltura partner id

Line 141: Kaltura admin secret

Line 144: Kaltura partner id


And pay attention to:

Line 91:  Collab Oauth timeout (minutes)

Line 145:  Kaltura Oauth timeout (seconds)

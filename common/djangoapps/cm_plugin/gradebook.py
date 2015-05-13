import requests
import json
from django.db.models.signals import pre_save
from django.dispatch import receiver
from cm_plugin.models import CmGradebook, CmGradebookRecords
from credentials import cm_credentials
import hashlib
from datetime import datetime, timedelta
import logging
log = logging.getLogger(__name__)

@receiver(pre_save, sender=CmGradebook)
def push_gradebook_to_savannah(sender, **kwargs):
    id = None
    last_updated_at = None
    instance = kwargs['instance']
    try:
        id = instance.id
        last_updated_at = instance.updated_at
    except:
        pass

    if id == None or last_updated_at == None:
        return None

    diff = get_diff_from_gradebook(id, last_updated_at)
    diff_json = format_diff_to_json(diff, instance)
    communicate_to_savannah(diff_json)

def get_diff_from_gradebook(gradebook_id, last_updated_at):
    gb = CmGradebook.objects.get(id=gradebook_id)
    # since I dont have a proper feedback mechanism from savannah to edx on gradebook failure yet,
    # sending diffs of past 4 hrs to savannah. Since rake task on savannah will be hourly, this should 
    # make sure that all data is safely sent to savannah. Should modify it to last updated once a 
    # proper feedback mechanism is setup
    gb_recs = CmGradebookRecords.objects.filter(cm_gradebook=gradebook_id).filter(updated_at__gte=(datetime.today() - timedelta(hours = 4)))

    return gb_recs

def format_diff_to_json(diff, gb):
    formatted_diff = []
    for item in diff:
        formatted_diff += [{'unit_name': item.unit_name, 'score': item.score,
                            'email': item.user_email}]

    if len(formatted_diff) == 0:
        formatted_diff = [{'no_records': 'no_records'}]

    return {'id': gb.course_id, 'records': formatted_diff}

def communicate_to_savannah(diff_json):
    shared_secret = cm_credentials('shared_secret').rstrip()
    api_key = cm_credentials('api_key').rstrip()
    lms_id = cm_credentials('lms_id')
    callback_url = cm_credentials('callback_url').rstrip()
    diff_json['lms_id'] = lms_id
    token = hashlib.sha256(shared_secret + "|" + str(lms_id)).hexdigest()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'X-Lms-Token': token, 'X-Api-Key': api_key}
    
    r = requests.post(callback_url + "/api/gradebook/import", json.dumps(diff_json), headers=headers)
    if r.status_code != 200:
        log.error("r.content")

import requests
import json
import time
import os

current_time = time.time()
yesterdays_time = current_time - 84600
tag_to_remove = '4726467'

IntercomUrl = 'https://api.intercom.io/contacts/search'
AccessToken = os.environ.get('AccessToken')
headers = {
    'Authorization': 'Bearer ' + AccessToken,
    'Accept': 'application/json'
}

SearchQuery = {
    'query': {
        'operator': 'AND',
        'value': [
            {
                'field': 'updated_at',
                'operator': '>',
                'value': yesterdays_time
            },
            {
                'field': 'tag_id',
                'operator': '=',
                'value': tag_to_remove
            }
        ]
    }
}


def remove_tag_from_contacts():
    contacts_ids = get_contacts_with_tag()

    for contact_id in contacts_ids:
        delete_tag_url = 'https://api.intercom.io/contacts/' + contact_id + '/tags/' + tag_to_remove
        r = requests.delete(delete_tag_url, headers=headers)
        print(r.status_code)
        print(r.text)
        print(r.headers)
    return print(str(len(contacts_ids)) + ' tags removed')


def get_contacts_with_tag():
    r = requests.post(IntercomUrl, headers=headers, json=SearchQuery)
    contacts_json = json.loads(r.text)
    number_of_pages = contacts_json['pages']['total_pages']

    if number_of_pages > 1:
        print('More than one page')
        contact_ids = multiple_pages_of_contact_ids(contacts_json)
    else:
        print('One page or less')
        contact_ids = one_page_of_contact_ids(contacts_json)

    return contact_ids


def one_page_of_contact_ids(contacts_json):
    contact_ids = []
    current_ids = get_contact_ids(contacts_json)
    contact_ids += current_ids
    return contact_ids


def multiple_pages_of_contact_ids(contacts_json):
    contact_ids = []
    current_ids = get_contact_ids(contacts_json)
    contact_ids += current_ids

    number_of_pages = contacts_json['pages']['total_pages']
    print(str(number_of_pages) + ' pages of contacts')
    print('Page 1 ids gathered')

    for request in range(1, number_of_pages):
        starting_after_token = contacts_json['pages']['next']['starting_after']

        pagination = {
            "pagination": {
                "starting_after": starting_after_token
            }
        }
        SearchQuery.update(pagination)
        r = requests.post(IntercomUrl, headers=headers, json=SearchQuery)
        contacts_json = json.loads(r.text)
        current_ids = get_contact_ids(contacts_json)
        contact_ids += current_ids

        if 'next' in contacts_json['pages']:
            starting_after_token = contacts_json['pages']['next']['starting_after']
            print('Page ' + str(request + 1) + ' ids gathered')
        else:
            print('Page ' + str(request + 1) + ' ids gathered')
    return contact_ids


def get_contact_ids(contacts_json):
    contact_ids = []
    contacts = contacts_json['data']

    for contact in contacts:
        current_id = contact['id']
        contact_ids.append(current_id)
    return contact_ids


if __name__ == '__main__':
    remove_tag_from_contacts()

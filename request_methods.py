import requests
begin_url = 'http://127.0.0.1:5050'


async def post_user_request(username):
    url = 'http://127.0.0.1:5050/user'
    payload = {
        'user_name': username
    }

    response = requests.post(url, json=payload)
    return response.json()


async def update_user_request(user_name, city_from=None, city_to=None):
    url = begin_url + '/user'
    payload = {
        'user_name': user_name,
        'city_from': city_from,
        'city_to': city_to
    }

    response = requests.patch(url, json=payload)
    return response.json()


async def post_find_group(city_from, city_to):
    url = begin_url + '/group/find'
    payload = {
        'city_from': city_from,
        'city_to': city_to
    }
    response = requests.post(url, json=payload)
    return response.json()


async def post_group_create(city_from, city_to, group_name, username):
    url = begin_url + '/group/create'
    payload = {
        "group_name": group_name,
        "city_from": city_from,
        "city_to": city_to,
        "user_name": username
    }
    response = requests.post(url, json=payload)
    return response.json()

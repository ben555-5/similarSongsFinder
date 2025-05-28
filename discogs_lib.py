import discogs_client

def get_client():
    d = discogs_client.Client('ExampleApplication/0.1', user_token="GVOasQPZopgGnCjiQpCQlsbIsvocZxzMkEsJNURq")
    return d
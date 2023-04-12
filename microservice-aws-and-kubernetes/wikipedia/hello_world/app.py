import json
import wikipediaapi

# prints when function loads
print('Loading function')


def lambda_handler(event, context):
    ''' Wikipedia page summarizer.
        :param event: a request with a wikipedia "entity" that has page information
        :return: a response that contains the first sentence of a wikipedia page,
            the response is JSON formatted.'''
    print(f"Event: {event}")
    # Init the Wikipedia API
    wiki_wiki = wikipediaapi.Wikipedia(language='en', timeout=60)
    ## TO DO: Check that the request has some input body and save it
    if 'body' in event:
        event = json.loads(event["body"])
    
    if 'entity' in event.keys():
    ## TO DO: Get the wikipedia "entity" from the body of the request
        entity = event["entity"]
    else:
        print("Missing entity in event")
        return 1
    
    page_entity = wiki_wiki.page(entity)
    print(f"Page {entity} - Exists: {page_entity.exists()}")
        
    if page_entity.exists():
        print(f"Page {entity} - Summary: {page_entity.summary.split('. ')[0]}.")
    
    print(f"context: {context}, event: {event}")
    ## TO DO: Format the response as JSON and return the result
    response = {
        "statusCode": 200,
        "headers": { "Content-type": "application/json" },
        "body": json.dumps({
            "Page - Exists": page_entity.exists(),
            "Page - Summary": f"{page_entity.summary.split('. ')[0]}." if page_entity.exists() else "None",
        })
    }
    
    return response

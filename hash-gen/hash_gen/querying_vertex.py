from google.cloud import aiplatform

# Set variables for the current deployed index.
INDEX_ENDPOINT_NAME = 'projects/226885687962/locations/northamerica-northeast1/indexEndpoints/5138888649806446592'
DEPLOYED_INDEX_ID = 'testingindex'
QUERY_EMBEDDING=[1,0,1,0,1,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,0,0,1,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,1,0,1,1,0,0,1,1,1,0,1] # this is sim1.json

# Fetch the endpoint
my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=INDEX_ENDPOINT_NAME
)

# Execute the request
response = my_index_endpoint.match(
    deployed_index_id=DEPLOYED_INDEX_ID,
    queries=[QUERY_EMBEDDING],
    # The number of nearest neighbors to be retrieved
    num_neighbors=4,
)

# Handle the response
print(response)
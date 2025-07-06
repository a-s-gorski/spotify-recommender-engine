#!/bin/bash

# Step 1: Get token
echo "Retrieving token..."
TOKEN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=admin&password=admin')

echo "Token response: $TOKEN_RESPONSE"

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to retrieve access token. Response was:"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

if [ "$REFRESH_TOKEN" == "null" ] || [ -z "$REFRESH_TOKEN" ]; then
  echo "Failed to retrieve refresh token. Response was:"
  echo "$TOKEN_RESPONSE"
  exit 1
fi

# echo "Access token retrieved: $ACCESS_TOKEN"
# echo "Refresh token retrieved: $REFRESH_TOKEN"

# Step 2: Call protected endpoint with the initial token
echo "Calling protected endpoint with initial access token..."
PROTECTED_RESPONSE_INITIAL=$(curl -s -X GET http://localhost:8000/auth/protected \
  -H "Authorization: Bearer $ACCESS_TOKEN")

# echo "Protected endpoint response (initial token): $PROTECTED_RESPONSE_INITIAL"

# Step 3: Refresh the token
echo "Refreshing access token..."
REFRESH_RESPONSE=$(curl -s -X POST 'http://localhost:8000/auth/refresh' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "refresh_token=$REFRESH_TOKEN")

echo "Refresh response: $REFRESH_RESPONSE"

NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access_token')

if [ "$NEW_ACCESS_TOKEN" == "null" ] || [ -z "$NEW_ACCESS_TOKEN" ]; then
  echo "Failed to refresh access token. Response was:"
  echo "$REFRESH_RESPONSE"
  exit 1
fi

echo "New access token: $NEW_ACCESS_TOKEN"

# Step 4: Call protected endpoint with the refreshed token
echo "Calling protected endpoint with refreshed access token..."
PROTECTED_RESPONSE_REFRESHED=$(curl -s -X GET http://localhost:8000/auth/protected \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN")

echo "Protected endpoint response (refreshed token): $PROTECTED_RESPONSE_REFRESHED"


echo "Calling /recommend/recommend-clustering endpoint..."

PLAYLIST_NAME="chill lofi beats"
K=10
N_NEIGHBORS=5

CLUSTERING_RESPONSE=$(curl -s -G "http://localhost:8000/recommend/recommend-clustering" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  --data-urlencode "playlist_name=$PLAYLIST_NAME" \
  --data-urlencode "k=$K" \
  --data-urlencode "n_neighbors=$N_NEIGHBORS")

echo "Clustering recommendation response: $CLUSTERING_RESPONSE"


echo "Calling /recommend/recommend-collaborative endpoint..."

# Seed track URIs for testing
QUERY_URI_1="spotify:track:7ouMYWpwJ422jRcDASZB7P"
QUERY_URI_2="spotify:track:1f6zKZ0I1ChZ0zsZt4AZqW"
K=10

COLLABORATIVE_RESPONSE=$(curl -s -G "http://localhost:8000/recommend/recommend-collaborative" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  --data-urlencode "query_uris=$QUERY_URI_1" \
  --data-urlencode "query_uris=$QUERY_URI_2" \
  --data-urlencode "k=$K")

echo "Collaborative recommendation response: $COLLABORATIVE_RESPONSE"


echo "Calling /recommend/recommend-hybrid endpoint..."

HYBRID_RESPONSE=$(curl -s -G "http://localhost:8000/recommend/recommend-hybrid" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  --data-urlencode "playlist_name=$PLAYLIST_NAME" \
  --data-urlencode "query_uris=$QUERY_URI_1" \
  --data-urlencode "query_uris=$QUERY_URI_2" \
  --data-urlencode "k=$K" \
  --data-urlencode "n_neighbors=$N_NEIGHBORS")

echo "Hybrid recommendation response: $HYBRID_RESPONSE"
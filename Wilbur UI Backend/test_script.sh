#!/bin/bash

# echo 'Adding first Google account'
# curl -k localhost:5000/google/add_account -X POST -H "Content-Type: application/json" --data '{"email":"ccc273@gmail.com"}'
# echo ''

# echo 'Adding second Google account'
# curl -k localhost:5000/google/add_account -X POST -H "Content-Type: application/json" --data '{"email":"conorc273@gmail.com"}'
# echo ''

# echo 'File search in Google account for "test"'
# curl -k localhost:5000/google/get_files -X GET -H "Content-Type: application/json" --data '{"email":"conorc273@gmail.com", "keyword":"test"}'
# echo ''

# echo 'File search in second Google account for "news"'
# curl -k localhost:5000/google/get_files -X GET -H "Content-Type: application/json" --data '{"email":"ccc273@gmail.com", "keyword":"news"}'
# echo ''

# echo 'Mail search in first Google account for "test"'
# curl -k localhost:5000/google/get_mail -X GET -H "Content-Type: application/json" --data '{"email":"conorc273@gmail.com", "keyword":"test"}'
# echo ''

# echo 'Mail search in second Google account for "news"'
# curl -k localhost:5000/google/get_mail -X GET -H "Content-Type: application/json" --data '{"email":"ccc273@gmail.com", "keyword":"news"}'
# echo ''

echo 'File search in Dropbox account for "test"'
curl -k localhost:5000/dropbox/get_files -X GET -H "Content-Type: application/json" --data '{"keyword":"test"}'
echo ''

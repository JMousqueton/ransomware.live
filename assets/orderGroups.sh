cp groups.json groups.json.ORIG
jq '.|=sort_by(.name)' groups.json.ORIG > groups.json

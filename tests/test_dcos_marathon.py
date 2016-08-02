#!/usr/bin/python

from dcos_marathon import DcosMarathon
import json

m = DcosMarathon("http://myserver.com", username=None, password=None, dcos=True)
print(str(m))

print(str(m.list_apps()))

# Test is Marathon reachable?
print("Marathon service is reachable: %s"%(str(m.is_reachable())))

# Validate schema
config = json.loads('{"id": "test"}')
m.validate_app_schema(config)

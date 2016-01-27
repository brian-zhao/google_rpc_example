from protorpc.wsgi import service

import postservice

# Map the RPC service and path (/PostService)
app = service.service_mappings([('/PostService', postservice.PostService)])
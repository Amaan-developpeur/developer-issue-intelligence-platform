from rest_framework.throttling import SimpleRateThrottle

class DashboardThrottle(SimpleRateThrottle):
    scope = "dashboard"  

    def get_cache_key(self, request, view):
        # Identify the client uniquely
        ident = None

        # If API key auth was used
        if hasattr(request, "api_key") and request.api_key:
            ident = f"apikey_{request.api_key.key}"
        else:
            # Fallback to IP if unauthenticated
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

# Add this in a new file: rate_limiting.py

from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

class CustomRateThrottle(UserRateThrottle):
    def parse_rate(self, rate):
        if rate is None:
            return (None, None)
        return super().parse_rate(rate)

class RateLimitMixin:
    """
    A mixin that adds rate limiting to APIView classes.
    """
    throttle_classes = (CustomRateThrottle,)
    rate = None

    def get_throttles(self):
        throttle_classes = self.throttle_classes
        if self.rate:
            for throttle_class in throttle_classes:
                throttle_class.rate = self.rate
        return [throttle() for throttle in throttle_classes]

import pytest
import stripe
from sentinel_api.services.stripe_client import StripeClient

def test_stripe_webhook_invalid_signature():
    payload = b'{"type": "checkout.session.completed"}'
    
    with pytest.raises(Exception, match="Invalid signature"):
        StripeClient.construct_webhook_event(payload, "invalid_sig")

# In a real environment, we would use responses or httpx.mock to mock 
# the outgoing requests to api.stripe.com. For the architecture demonstration,
# we ensure the service gracefully handles missing keys instead of hard crashing.
def test_stripe_checkout_no_keys():
    with pytest.raises(Exception):
        StripeClient.create_checkout_session("cus_123", "price_123", "http://ok", "http://cancel", "org_123")

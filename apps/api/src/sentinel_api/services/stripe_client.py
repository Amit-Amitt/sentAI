import stripe
from typing import Dict, Any, Optional
import structlog
from sentinel_api.config.settings import settings

logger = structlog.get_logger("sentinel_api.services.stripe_client")

# Initialize SDK
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeClient:
    """Wrapper around the official Stripe SDK."""
    
    @staticmethod
    def create_checkout_session(
        customer_id: str, 
        price_id: str, 
        success_url: str, 
        cancel_url: str, 
        client_reference_id: str
    ) -> str:
        """Generates a Stripe Checkout Session URL for subscribing to a plan."""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=client_reference_id,
            )
            return session.url
        except Exception as e:
            logger.error("Failed to create Stripe checkout session", error=str(e))
            raise e

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> str:
        """Generates a Stripe Customer Portal URL for managing billing."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session.url
        except Exception as e:
            logger.error("Failed to create Stripe portal session", error=str(e))
            raise e

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> stripe.Event:
        """Verifies the webhook signature and returns the Event object."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            # Invalid payload
            raise Exception("Invalid payload") from e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise Exception("Invalid signature") from e

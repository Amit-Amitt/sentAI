import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class BillingPlan(BaseModel):
    """Configurable definitions of Tiers (e.g., Free, Starter, Pro, Enterprise)."""
    __tablename__ = "billing_plans"

    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    
    # E.g. {"max_users": 5, "max_projects": 3, "telemetry_events_per_month": 1000000}
    quotas: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    
    # E.g. {"can_use_remediation": False, "can_use_sso": False}
    features: Mapped[Dict[str, bool]] = mapped_column(JSON, default=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class BillingCustomer(BaseModel):
    """Maps an Organization to a Stripe Customer ID."""
    __tablename__ = "billing_customers"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    stripe_customer_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    billing_email: Mapped[str] = mapped_column(String, nullable=False)
    
    subscription = relationship("BillingSubscription", back_populates="customer", uselist=False, lazy="selectin")


class BillingSubscription(BaseModel):
    """Tracks active Stripe subscription state."""
    __tablename__ = "billing_subscriptions"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("billing_customers.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False)
    
    stripe_subscription_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String, nullable=False) # active, trialing, past_due, canceled, incomplete
    
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    customer = relationship("BillingCustomer", back_populates="subscription")
    plan = relationship("BillingPlan", lazy="selectin")


class BillingInvoice(BaseModel):
    """Stores invoice metadata from Stripe."""
    __tablename__ = "billing_invoices"

    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("billing_customers.id", ondelete="CASCADE"), index=True, nullable=False)
    stripe_invoice_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    amount_due: Mapped[int] = mapped_column(Integer, nullable=False) # in cents
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False) # in cents
    currency: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[str] = mapped_column(String, nullable=False) # draft, open, paid, uncollectible, void
    hosted_invoice_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    invoice_pdf: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class UsageRecord(BaseModel):
    """High-throughput table to track daily consumption metrics per organization."""
    __tablename__ = "usage_records"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String, index=True, nullable=False) # e.g., 'telemetry_events', 'api_calls'
    
    # Store aggregated totals per day to keep the table size manageable
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class WebhookEvent(BaseModel):
    """Idempotency tracking for Stripe Webhooks."""
    __tablename__ = "webhook_events"

    stripe_event_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False) # pending, processed, failed
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

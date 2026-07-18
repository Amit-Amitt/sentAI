# Kubernetes Deployment Guide

This guide walks you through deploying Sentinel AI to a production Kubernetes cluster using Helm.

## Prerequisites
1. Kubernetes cluster (v1.28+)
2. Helm v3 installed locally
3. An external PostgreSQL 15+ database
4. An external Redis 7+ cluster

## 1. Create Secrets
First, create the Kubernetes secret holding the sensitive environment variables.

```yaml
# sentinel-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentinel-secrets
type: Opaque
stringData:
  SENTINEL_DATABASE_URL: "postgresql://..."
  SENTINEL_REDIS_URL: "redis://..."
  SENTINEL_JWT_SECRET: "your-very-secure-jwt-secret"
  SENTINEL_AUTH_ENCRYPTION_KEY: "your-very-secure-encryption-key"
  SENTINEL_STRIPE_SECRET_KEY: "sk_live_..."
```
Apply it: `kubectl apply -f sentinel-secrets.yaml`

## 2. Configure Helm Values
Create a custom `values-prod.yaml` overriding the defaults in `deploy/helm/sentinel-ai/values.yaml`.

```yaml
env:
  envFromSecretName: "sentinel-secrets"
  SENTINEL_APP_ENV: "production"

ingress:
  hosts:
    - host: api.yourcompany.com
      paths:
        - path: /
          pathType: ImplementationSpecific
          backend:
            service:
              name: sentinel-api
              port:
                number: 80
```

## 3. Install the Chart
Install or upgrade the Sentinel AI platform:

```bash
helm upgrade --install sentinel-ai ./deploy/helm/sentinel-ai \
  -f values-prod.yaml \
  --namespace sentinel \
  --create-namespace
```

## 4. Verify Deployment
Check that pods are spinning up and passing their Liveness/Readiness probes:
```bash
kubectl get pods -n sentinel
kubectl get ingress -n sentinel
```

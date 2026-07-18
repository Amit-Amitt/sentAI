def mask_secret(secret: str | None) -> str:
    """Masks a secret for safe logging.
    
    If the secret is None or empty, returns '*not set*'.
    If the secret is shorter than 6 characters, returns '***'.
    Otherwise, shows the first 3 and last 3 characters, masking the rest.
    """
    if not secret:
        return "*not set*"
        
    if len(secret) < 6:
        return "***"
        
    return f"{secret[:3]}***{secret[-3:]}"

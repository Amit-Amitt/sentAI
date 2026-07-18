import { describe, it, expect } from 'vitest';
import { sanitize } from '../src/sanitizer';

describe('Sanitizer', () => {
  it('should mask sensitive keys', () => {
    const data = {
      username: 'johndoe',
      password: 'supersecretpassword123',
      api_key: 'sent_abcdefg',
      authorization: 'Bearer 1234',
      nested: {
        token: 'xyz',
        public: 'info'
      }
    };

    const sanitized = sanitize(data);
    
    expect(sanitized.username).toBe('johndoe');
    expect(sanitized.password).toBe('[REDACTED]');
    expect(sanitized.api_key).toBe('[REDACTED]');
    expect(sanitized.authorization).toBe('[REDACTED]');
    expect(sanitized.nested.token).toBe('[REDACTED]');
    expect(sanitized.nested.public).toBe('info');
  });

  it('should handle arrays', () => {
    const data = [
      { secret: 'hidden', visible: 'seen' },
      { test: 'ok' }
    ];

    const sanitized = sanitize(data);
    expect(sanitized[0].secret).toBe('[REDACTED]');
    expect(sanitized[0].visible).toBe('seen');
  });

  it('should ignore non-objects', () => {
    expect(sanitize('string')).toBe('string');
    expect(sanitize(123)).toBe(123);
    expect(sanitize(null)).toBe(null);
  });
});

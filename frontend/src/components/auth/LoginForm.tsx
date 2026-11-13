import React, { useState } from 'react';
import { Button, TextInput, InlineNotification } from '@carbon/react';
import { useAuth } from '../../lib/auth-context';
import { ApiClientError } from '../../lib/api-client';

export function LoginForm() {
  const [email, setEmail] = useState('procurement_reviewer@example.com');
  const [password, setPassword] = useState('Password123!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <InlineNotification
          kind="error"
          title="Login failed"
          subtitle={error}
          lowContrast
          hideCloseButton
        />
      )}

      <TextInput
        id="email"
        labelText="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        disabled={loading}
      />

      <TextInput
        id="password"
        labelText="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        disabled={loading}
      />

      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Logging in...' : 'Login'}
      </Button>

      <div className="text-sm text-gray-600">
        <p>Default credentials:</p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>procurement_reviewer@example.com</li>
          <li>longlist_finalization_owner@example.com</li>
          <li>business_unit_collaborator@example.com</li>
        </ul>
        <p className="mt-2">Password: Password123!</p>
      </div>
    </form>
  );
}

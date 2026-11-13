import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { useAuth } from '../lib/auth-context';

export function LoginPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      navigate('/', { replace: true });
    }
  }, [token, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white shadow-lg rounded-lg">
        <div>
          <h1 className="text-3xl font-bold text-center text-gray-900">
            Deutsche Telekom
          </h1>
          <h2 className="mt-2 text-xl text-center text-gray-600">
            Procurement Workflow
          </h2>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}

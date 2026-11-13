import { Header as CarbonHeader, HeaderName, HeaderGlobalBar, HeaderGlobalAction } from '@carbon/react';
import { Logout } from '@carbon/icons-react';
import { useAuth } from '../../lib/auth-context';
import { useNavigate } from 'react-router-dom';

export function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <CarbonHeader aria-label="Deutsche Telekom Procurement">
      <HeaderName href="/" prefix="">
        Deutsche Telekom Procurement
      </HeaderName>
      <HeaderGlobalBar>
        {user && (
          <span className="flex items-center px-4 text-sm text-gray-300">
            {user.email}
          </span>
        )}
        <HeaderGlobalAction
          aria-label="Logout"
          onClick={handleLogout}
          tooltipAlignment="end"
        >
          <Logout size={20} />
        </HeaderGlobalAction>
      </HeaderGlobalBar>
    </CarbonHeader>
  );
}

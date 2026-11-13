import { SideNav, SideNavItems, SideNavLink } from '@carbon/react';
import { Dashboard, DocumentMultiple_01, CheckmarkOutline, Send, Upload, Export, DataBase, Search, Checkmark, Locked } from '@carbon/icons-react';
import { useLocation } from 'react-router-dom';

export function Sidebar() {
  const location = useLocation();

  return (
    <SideNav aria-label="Side navigation" isFixedNav expanded isChildOfHeader={false}>
      <SideNavItems>
        <SideNavLink
          renderIcon={Dashboard}
          href="/"
          isActive={location.pathname === '/'}
        >
          Dashboard
        </SideNavLink>
        <SideNavLink
          renderIcon={Upload}
          href="/intake"
          isActive={location.pathname.startsWith('/intake')}
        >
          Intake
        </SideNavLink>
        <SideNavLink
          renderIcon={DocumentMultiple_01}
          href="/needs"
          isActive={location.pathname.startsWith('/needs')}
        >
          Needs
        </SideNavLink>
        <SideNavLink
          renderIcon={CheckmarkOutline}
          href="/reviews"
          isActive={location.pathname.startsWith('/reviews')}
        >
          Reviews
        </SideNavLink>
        <SideNavLink
          renderIcon={DataBase}
          href="/evidence"
          isActive={location.pathname.startsWith('/evidence')}
        >
          Evidence
        </SideNavLink>
        <SideNavLink
          renderIcon={Search}
          href="/research"
          isActive={location.pathname.startsWith('/research')}
        >
          Research
        </SideNavLink>
        <SideNavLink
          renderIcon={Export}
          href="/vms-handoff"
          isActive={location.pathname.startsWith('/vms-handoff')}
        >
          VMS Handoff
        </SideNavLink>
        <SideNavLink
          renderIcon={Checkmark}
          href="/validation"
          isActive={location.pathname.startsWith('/validation')}
        >
          Validation
        </SideNavLink>
        <SideNavLink
          renderIcon={Locked}
          href="/lock-dispatch"
          isActive={location.pathname.startsWith('/lock-dispatch')}
        >
          Lock & Dispatch
        </SideNavLink>
        <SideNavLink
          renderIcon={Send}
          href="/dispatch"
          isActive={location.pathname.startsWith('/dispatch')}
        >
          Dispatch
        </SideNavLink>
      </SideNavItems>
    </SideNav>
  );
}

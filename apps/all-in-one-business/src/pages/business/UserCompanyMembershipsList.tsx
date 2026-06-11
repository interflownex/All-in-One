import React from 'react';
import SmartCRUD from '../../components/SmartCRUD';

const UserCompanyMembershipsList: React.FC = () => {
  return (
    <SmartCRUD 
      module="business" 
      entity="usercompanymemberships" 
      type="list" 
      title="User Company Memberships" 
    />
  );
};

export default UserCompanyMembershipsList;

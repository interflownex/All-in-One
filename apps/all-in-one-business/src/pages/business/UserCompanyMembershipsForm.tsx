import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const UserCompanyMembershipsForm: React.FC = () => {
  return (
    <SmartCRUD
      module="business"
      entity="usercompanymemberships"
      type="form"
      title="User Company Memberships"
    />
  );
};

export default UserCompanyMembershipsForm;

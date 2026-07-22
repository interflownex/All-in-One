import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AccessPoliciesList: React.FC = () => {
  return (
    <SmartCRUD module="permissions" entity="accesspolicies" type="list" title="Access Policies" />
  );
};

export default AccessPoliciesList;

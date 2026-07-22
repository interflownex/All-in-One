import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ApprovalLimitsList: React.FC = () => {
  return (
    <SmartCRUD module="permissions" entity="approvallimits" type="list" title="Approval Limits" />
  );
};

export default ApprovalLimitsList;

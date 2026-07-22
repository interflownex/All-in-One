import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RetentionPoliciesForm: React.FC = () => {
  return (
    <SmartCRUD
      module="document"
      entity="retentionpolicies"
      type="form"
      title="Retention Policies"
    />
  );
};

export default RetentionPoliciesForm;

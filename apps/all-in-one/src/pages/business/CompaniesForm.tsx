import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CompaniesForm: React.FC = () => {
  return <SmartCRUD module="business" entity="companies" type="form" title="Companies" />;
};

export default CompaniesForm;

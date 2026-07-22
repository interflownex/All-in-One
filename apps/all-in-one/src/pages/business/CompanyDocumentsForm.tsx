import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const CompanyDocumentsForm: React.FC = () => {
  return (
    <SmartCRUD module="business" entity="companydocuments" type="form" title="Company Documents" />
  );
};

export default CompanyDocumentsForm;

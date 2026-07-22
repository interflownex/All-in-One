import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const InsuranceOptionsList: React.FC = () => {
  return (
    <SmartCRUD module="delivery" entity="insuranceoptions" type="list" title="Insurance Options" />
  );
};

export default InsuranceOptionsList;

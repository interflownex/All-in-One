import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const InsuranceOptionsForm: React.FC = () => {
  return (
    <SmartCRUD module="delivery" entity="insuranceoptions" type="form" title="Insurance Options" />
  );
};

export default InsuranceOptionsForm;

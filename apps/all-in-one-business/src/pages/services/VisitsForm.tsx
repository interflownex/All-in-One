import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const VisitsForm: React.FC = () => {
  return <SmartCRUD module="services" entity="visits" type="form" title="Visits" />;
};

export default VisitsForm;

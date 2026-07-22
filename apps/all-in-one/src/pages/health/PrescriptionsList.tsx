import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PrescriptionsList: React.FC = () => {
  return <SmartCRUD module="health" entity="prescriptions" type="list" title="Prescriptions" />;
};

export default PrescriptionsList;

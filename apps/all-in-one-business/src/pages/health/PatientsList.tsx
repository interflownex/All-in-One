import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PatientsList: React.FC = () => {
  return <SmartCRUD module="health" entity="patients" type="list" title="Patients" />;
};

export default PatientsList;

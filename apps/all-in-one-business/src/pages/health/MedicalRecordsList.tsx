import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const MedicalRecordsList: React.FC = () => {
  return <SmartCRUD module="health" entity="medicalrecords" type="list" title="Medical Records" />;
};

export default MedicalRecordsList;

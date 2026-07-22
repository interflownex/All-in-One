import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const MedicalRecordsForm: React.FC = () => {
  return <SmartCRUD module="health" entity="medicalrecords" type="form" title="Medical Records" />;
};

export default MedicalRecordsForm;

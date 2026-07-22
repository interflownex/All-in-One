import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const AppointmentsForm: React.FC = () => {
  return <SmartCRUD module="health" entity="appointments" type="form" title="Appointments" />;
};

export default AppointmentsForm;

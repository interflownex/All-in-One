import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const TicketsForm: React.FC = () => {
  return <SmartCRUD module="mobility" entity="tickets" type="form" title="Tickets" />;
};

export default TicketsForm;

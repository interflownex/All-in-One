import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DeliveryRequestsForm: React.FC = () => {
  return (
    <SmartCRUD module="delivery" entity="deliveryrequests" type="form" title="Delivery Requests" />
  );
};

export default DeliveryRequestsForm;

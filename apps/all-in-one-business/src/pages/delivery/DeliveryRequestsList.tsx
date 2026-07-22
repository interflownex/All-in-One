import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DeliveryRequestsList: React.FC = () => {
  return (
    <SmartCRUD module="delivery" entity="deliveryrequests" type="list" title="Delivery Requests" />
  );
};

export default DeliveryRequestsList;

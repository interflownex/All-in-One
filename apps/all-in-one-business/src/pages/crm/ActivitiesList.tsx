import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ActivitiesList: React.FC = () => {
  return <SmartCRUD module="crm" entity="activities" type="list" title="Activities" />;
};

export default ActivitiesList;

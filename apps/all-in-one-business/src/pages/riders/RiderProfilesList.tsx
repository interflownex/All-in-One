import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RiderProfilesList: React.FC = () => {
  return <SmartCRUD module="riders" entity="riderprofiles" type="list" title="Rider Profiles" />;
};

export default RiderProfilesList;

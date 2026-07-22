import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RiderDocumentsList: React.FC = () => {
  return <SmartCRUD module="riders" entity="riderdocuments" type="list" title="Rider Documents" />;
};

export default RiderDocumentsList;

import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DocumentOverview: React.FC = () => {
  return <SmartCRUD module="document" entity="document" type="list" title="Document" />;
};

export default DocumentOverview;

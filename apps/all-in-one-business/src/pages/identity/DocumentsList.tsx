import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DocumentsList: React.FC = () => {
  return <SmartCRUD module="identity" entity="documents" type="list" title="Documents" />;
};

export default DocumentsList;

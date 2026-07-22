import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DocumentsList: React.FC = () => {
  return <SmartCRUD module="document" entity="documents" type="list" title="Documents" />;
};

export default DocumentsList;

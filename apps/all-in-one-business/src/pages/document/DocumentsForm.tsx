import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DocumentsForm: React.FC = () => {
  return <SmartCRUD module="document" entity="documents" type="form" title="Documents" />;
};

export default DocumentsForm;

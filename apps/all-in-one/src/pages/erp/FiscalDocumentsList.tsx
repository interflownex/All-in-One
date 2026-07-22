import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FiscalDocumentsList: React.FC = () => {
  return <SmartCRUD module="erp" entity="fiscaldocuments" type="list" title="Fiscal Documents" />;
};

export default FiscalDocumentsList;

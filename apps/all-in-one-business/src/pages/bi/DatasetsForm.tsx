import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DatasetsForm: React.FC = () => {
  return <SmartCRUD module="bi" entity="datasets" type="form" title="Datasets" />;
};

export default DatasetsForm;

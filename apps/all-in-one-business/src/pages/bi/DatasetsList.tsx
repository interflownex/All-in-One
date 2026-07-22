import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const DatasetsList: React.FC = () => {
  return <SmartCRUD module="bi" entity="datasets" type="list" title="Datasets" />;
};

export default DatasetsList;

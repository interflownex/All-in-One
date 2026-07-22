import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const FoldersList: React.FC = () => {
  return <SmartCRUD module="document" entity="folders" type="list" title="Folders" />;
};

export default FoldersList;

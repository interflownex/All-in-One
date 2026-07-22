import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RecordingsList: React.FC = () => {
  return <SmartCRUD module="vision" entity="recordings" type="list" title="Recordings" />;
};

export default RecordingsList;

import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const RecordingsForm: React.FC = () => {
  return <SmartCRUD module="vision" entity="recordings" type="form" title="Recordings" />;
};

export default RecordingsForm;

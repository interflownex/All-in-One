import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const StreamsForm: React.FC = () => {
  return <SmartCRUD module="vision" entity="streams" type="form" title="Streams" />;
};

export default StreamsForm;

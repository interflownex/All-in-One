import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const BiometricsForm: React.FC = () => {
  return <SmartCRUD module="identity" entity="biometrics" type="form" title="Biometrics" />;
};

export default BiometricsForm;

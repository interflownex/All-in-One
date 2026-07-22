import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const PickingWavesList: React.FC = () => {
  return <SmartCRUD module="wms" entity="pickingwaves" type="list" title="Picking Waves" />;
};

export default PickingWavesList;

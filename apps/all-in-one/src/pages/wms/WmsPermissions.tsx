import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const WmsPermissions: React.FC = () => {
  return <SmartCRUD module="wms" entity="wmspermissions" type="list" title="Wms Permissões" />;
};

export default WmsPermissions;

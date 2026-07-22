import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const VisionPermissions: React.FC = () => {
  return (
    <SmartCRUD module="vision" entity="visionpermissions" type="list" title="Vision Permissões" />
  );
};

export default VisionPermissions;

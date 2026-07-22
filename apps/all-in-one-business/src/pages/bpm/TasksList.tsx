import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const TasksList: React.FC = () => {
  return <SmartCRUD module="bpm" entity="tasks" type="list" title="Tasks" />;
};

export default TasksList;

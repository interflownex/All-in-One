import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const TasksForm: React.FC = () => {
  return <SmartCRUD module="bpm" entity="tasks" type="form" title="Tasks" />;
};

export default TasksForm;

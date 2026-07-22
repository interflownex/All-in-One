import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const VacancySearch: React.FC = () => {
  return <SmartCRUD module="jobs" entity="vacancysearch" type="form" title="Vacancy Search" />;
};

export default VacancySearch;

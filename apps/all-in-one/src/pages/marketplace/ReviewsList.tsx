import React from "react";
import SmartCRUD from "../../components/SmartCRUD";

const ReviewsList: React.FC = () => {
  return <SmartCRUD module="marketplace" entity="reviews" type="list" title="Reviews" />;
};

export default ReviewsList;

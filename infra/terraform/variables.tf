variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "all-in-one-498012"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "network_name" {
  description = "VPC Network Name"
  type        = string
  default     = "all-in-one-vpc"
}

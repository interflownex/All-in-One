resource "google_compute_network" "vpc_network" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.network_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "all-in-one-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_alloydb_cluster" "main" {
  cluster_id = "all-in-one-cluster"
  location   = var.region
  network    = google_compute_network.vpc_network.id

  initial_user {
    password = "change-me-in-secret-manager" # Em producao, use Secret Manager
  }
  
  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_alloydb_instance" "main_instance" {
  cluster       = google_alloydb_cluster.main.name
  instance_id   = "all-in-one-instance-primary"
  instance_type = "PRIMARY"

  machine_config {
    cpu_count = 2
  }
}

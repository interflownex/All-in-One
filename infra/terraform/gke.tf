resource "google_container_cluster" "primary" {
  name     = "all-in-one-gke"
  location = var.region

  # Removendo o default node pool para usar um gerenciado separadamente
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc_network.id
  subnetwork = google_compute_subnetwork.subnet.id

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/16"
    services_ipv4_cidr_block = "/22"
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "all-in-one-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    preemptible  = true
    machine_type = "e2-standard-4"

    labels = {
      env = "staging"
    }

    # Workload Identity
    service_account = "default" # Em producao, use uma service account dedicada
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

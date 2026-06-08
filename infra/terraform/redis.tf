resource "google_redis_instance" "cache" {
  name               = "all-in-one-cache"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  location_id        = var.zone
  authorized_network = google_compute_network.vpc_network.id

  redis_version = "REDIS_7_0"
  display_name  = "All-in-One Redis Cache"

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

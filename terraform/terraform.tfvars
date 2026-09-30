location = "Australia East"

resource_group_name = "koalatech-hd-rg"

acr_name             = "koalatechhdacr0923"
storage_account_name = "koalatechhd0923"

aks_cluster_name = "koalatech-hd-aks"
aks_dns_prefix   = "koalatech-hd"

aks_node_count   = 3
aks_node_vm_size = "Standard_D2s_v6"

environment = "development"

tags = {
  Project     = "KoalaTech Course Platform"
  ManagedBy   = "Terraform"
  Practical   = "Task10.3HD"
  Environment = "Development"
  HDFeature   = "Infrastructure Drift Detection"
}
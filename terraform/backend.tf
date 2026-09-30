terraform {
  backend "azurerm" {
    resource_group_name  = "koalatech-hd-tfstate-rg"
    storage_account_name = "koalatechhdtf0923"
    container_name       = "tfstate"
    key                  = "koalatech-hd.tfstate"

    use_azuread_auth = true
    use_cli          = true
  }
}
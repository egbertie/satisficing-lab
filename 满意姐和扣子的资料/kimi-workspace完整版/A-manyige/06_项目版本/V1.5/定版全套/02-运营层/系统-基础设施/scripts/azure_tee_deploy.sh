#!/bin/bash
# Azure TEE Confidential Computing Instance Deployment Script
# This script deploys a Standard_DC8s_v3 VM with Intel TDX support

set -e

echo "=== Azure TEE机密计算实例部署脚本 ==="

# 1. Login to Azure (uncomment the appropriate method)
# Method 1: Interactive login (for local development)
# az login

# Method 2: Service Principal (for CI/CD automation)
# az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

# Method 3: Managed Identity (for Azure VM/Container)
# az login --identity

# 2. Set variables
RESOURCE_GROUP="satisficing-rg"
LOCATION="eastus"  # DCsv3 available in: eastus, westeurope, uksouth, etc.
VM_NAME="tee-vm-dc8sv3"
VM_SIZE="Standard_DC8s_v3"
ADMIN_USERNAME="azureuser"
# Generate SSH key if not exists
SSH_KEY_PATH="$HOME/.ssh/id_rsa_tee"

# 3. Create Resource Group
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# 4. Create Virtual Network and Subnet
echo "Creating virtual network..."
az network vnet create \
    --resource-group $RESOURCE_GROUP \
    --name ${VM_NAME}-vnet \
    --subnet-name default

# 5. Create Public IP
echo "Creating public IP..."
az network public-ip create \
    --resource-group $RESOURCE_GROUP \
    --name ${VM_NAME}-pip \
    --sku Standard \
    --allocation-method Static

# 6. Create Network Security Group
echo "Creating network security group..."
az network nsg create \
    --resource-group $RESOURCE_GROUP \
    --name ${VM_NAME}-nsg

# Allow SSH
az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name ${VM_NAME}-nsg \
    --name AllowSSH \
    --protocol Tcp \
    --priority 100 \
    --destination-port-range 22 \
    --access Allow

# 7. Create Network Interface
echo "Creating network interface..."
az network nic create \
    --resource-group $RESOURCE_GROUP \
    --name ${VM_NAME}-nic \
    --vnet-name ${VM_NAME}-vnet \
    --subnet default \
    --public-ip-address ${VM_NAME}-pip \
    --network-security-group ${VM_NAME}-nsg

# 8. Generate SSH key pair if not exists
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N ""
fi

SSH_PUBLIC_KEY=$(cat ${SSH_KEY_PATH}.pub)

# 9. Deploy DC8s_v3 Confidential VM
echo "Deploying Standard_DC8s_v3 Confidential VM..."
az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --size $VM_SIZE \
    --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest \
    --nics ${VM_NAME}-nic \
    --admin-username $ADMIN_USERNAME \
    --ssh-key-values "$SSH_PUBLIC_KEY" \
    --security-type ConfidentialVM \
    --enable-vtpm true \
    --enable-secure-boot true \
    --os-disk-security-encryption-type VMGuestStateOnly

echo "=== VM Deployment Complete ==="

# 10. Get VM details
echo "Fetching VM details..."
VM_IP=$(az network public-ip show \
    --resource-group $RESOURCE_GROUP \
    --name ${VM_NAME}-pip \
    --query ipAddress \
    --output tsv)

echo ""
echo "=== Deployment Summary ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "VM Name: $VM_NAME"
echo "VM Size: $VM_SIZE"
echo "Public IP: $VM_IP"
echo "SSH Key: $SSH_KEY_PATH"
echo ""
echo "To connect: ssh -i $SSH_KEY_PATH $ADMIN_USERNAME@$VM_IP"

# Save deployment info
cat > tee_deployment_info.txt << EOF
Azure TEE Deployment Information
================================
Resource Group: $RESOURCE_GROUP
VM Name: $VM_NAME
VM Size: $VM_SIZE
Location: $LOCATION
Public IP: $VM_IP
Admin User: $ADMIN_USERNAME
SSH Key: $SSH_KEY_PATH
Created: $(date)
EOF

echo "Deployment information saved to tee_deployment_info.txt"

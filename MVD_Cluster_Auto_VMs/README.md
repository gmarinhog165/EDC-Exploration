
# Cluster Setup Documentation

## Overview
This script sets up a Kubernetes cluster using Terraform and Ansible. It provisions MetalLB for load balancing and NGINX Ingress Controller for managing ingress traffic. The script also runs additional Terraform configuration for pods and seeds the cluster with initial configuration.

## Breakdown of the Script

### Local Provider
```hcl
provider "local" {
  # No specific configuration needed for the local provider
}
```
This section initializes the local provider, which is used to run local commands on the host machine.

### Run Ansible Playbook
```hcl
resource "null_resource" "run_ansible" {
  provisioner "local-exec" {
    command = "ansible-playbook -i ./Cluster/hosts ./Cluster/install_k8s.yml"
    environment = {
      ANSIBLE_CONFIG = "./Cluster/ansible.cfg"
    }
  }
}
```
This resource runs an Ansible playbook that installs Kubernetes on the cluster. It uses the inventory file located at `./Cluster/hosts` and the Ansible configuration file at `./Cluster/ansible.cfg`. You can modify the network interface `m_iface` in the `group_vars`, the hosts in the `hosts` file, and the SSH user in `ansible.cfg`.

### Apply MetalLB Manifest
```hcl
resource "null_resource" "apply_metallb" {
  provisioner "local-exec" {
    command = "kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.10/config/manifests/metallb-native.yaml"
  }

  depends_on = [null_resource.run_ansible]
}
```
This step applies the MetalLB manifest to the cluster. MetalLB is a load balancer implementation for bare-metal Kubernetes clusters.

### Apply MetalLB Configuration
```hcl
resource "null_resource" "apply_metallb_config" {
  provisioner "local-exec" {
    command = <<EOT
      # Wait for MetalLB pods to be running
      kubectl wait --namespace metallb-system 
        --for=condition=Ready 
        --timeout=300s 
        pod -l app=metallb

      # Apply the MetalLB configuration
      kubectl apply -f ./Cluster/metallb-config.yaml
    EOT
  }

  depends_on = [null_resource.apply_metallb]
}
```
This resource waits for the MetalLB pods to be in a `Ready` state and then applies the MetalLB configuration file (`metallb-config.yaml`).

### Apply NGINX Ingress Controller
```hcl
resource "null_resource" "apply_nginx_ingress" {
  provisioner "local-exec" {
    command = "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"
  }

  depends_on = [null_resource.apply_metallb_config]
}
```
This step installs the NGINX Ingress Controller, which manages inbound traffic to the cluster.

### Wait for NGINX Ingress Controller Pods
```hcl
resource "null_resource" "wait_for_nginx_ingress" {
  provisioner "local-exec" {
    command = <<EOT
      # Wait for NGINX Ingress Controller pods to be running
      kubectl wait --namespace ingress-nginx 
        --for=condition=ready pod 
        --selector=app.kubernetes.io/component=controller 
        --timeout=150s
    EOT
  }

  depends_on = [null_resource.apply_nginx_ingress]
}
```
This resource waits for the NGINX Ingress Controller pods to be in a `Ready` state before proceeding to the next step.

### Run Terraform for Pods
```hcl
resource "null_resource" "run_terraform_in_pods" {
  provisioner "local-exec" {
    command = <<EOT
      cd ./Pods
      terraform init
      terraform apply -auto-approve
    EOT
  }

  depends_on = [null_resource.wait_for_nginx_ingress]
}
```
After NGINX Ingress is ready, this step runs Terraform in the `./Pods` directory to apply further configuration related to the pods.

### Label All Nodes for Ingress
```hcl
resource "null_resource" "label_nodes" {
  provisioner "local-exec" {
    command = <<EOT
      # Get all nodes and label them
      kubectl get nodes -o name | xargs -I {} kubectl label {} ingress-ready=true
    EOT
  }

  depends_on = [null_resource.wait_for_nginx_ingress]
}
```
This resource labels all Kubernetes nodes with `ingress-ready=true`, preparing them to handle ingress traffic.

### Seed the Cluster
```hcl
resource "null_resource" "run_seed_k8s" {
  provisioner "local-exec" {
    command = "./seed-k8s.sh"
  }

  depends_on = [null_resource.run_terraform_in_pods]
}
```
Finally, this resource runs the `seed-k8s.sh` script to seed the cluster with any required resources or configurations.

## Customizing the Ansible Playbook
- **m_iface**: You can modify the network interface used by Kubernetes in the `group_vars` file.
- **Hosts**: The hosts for the Kubernetes cluster are defined in the `hosts` file.
- **SSH User**: The SSH user for Ansible can be configured in the `ansible.cfg` file.

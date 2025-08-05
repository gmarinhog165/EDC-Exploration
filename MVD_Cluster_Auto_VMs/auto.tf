provider "local" {
  # No specific configuration needed for the local provider
}

resource "null_resource" "run_ansible" {
  provisioner "local-exec" {
    command = "ansible-playbook -i ./Cluster/hosts ./Cluster/install_k8s.yml"
    
    environment = {
      ANSIBLE_CONFIG = "./Cluster/ansible.cfg"
    }
  }
}

# Apply the MetalLB manifest
resource "null_resource" "apply_metallb" {
  provisioner "local-exec" {
    command = "kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.10/config/manifests/metallb-native.yaml"
  }

  depends_on = [null_resource.run_ansible]
}

# Apply the MetalLB configuration
resource "null_resource" "apply_metallb_config" {
  provisioner "local-exec" {
    command = <<EOT
      # Wait for MetalLB pods to be running
      kubectl wait --namespace metallb-system \
        --for=condition=Ready \
        --timeout=300s \
        pod -l app=metallb

      # Apply the MetalLB configuration
      kubectl apply -f ./Cluster/metallb-config.yaml
    EOT
  }

  depends_on = [null_resource.apply_metallb]
}
# Apply the NGINX Ingress Controller manifest
resource "null_resource" "apply_nginx_ingress" {
  provisioner "local-exec" {
    command = "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"
  }

  depends_on = [null_resource.apply_metallb_config]
}

# Wait for the NGINX Ingress Controller pods to be running
resource "null_resource" "wait_for_nginx_ingress" {
  provisioner "local-exec" {
    command = <<EOT
      # Wait for NGINX Ingress Controller pods to be running
      kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=150s
    EOT
  }

  depends_on = [null_resource.apply_nginx_ingress]
}

# Run Terraform in the ./Pods directory after NGINX Ingress is running
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

# Label all nodes with "ingress-ready=true"
resource "null_resource" "label_nodes" {
  provisioner "local-exec" {
    command = <<EOT
      # Get all nodes and label them
      kubectl get nodes -o name | xargs -I {} kubectl label {} ingress-ready=true
    EOT
  }

  depends_on = [null_resource.wait_for_nginx_ingress]
}

resource "null_resource" "run_seed_k8s" {
  provisioner "local-exec" {
    command = "./seed-k8s.sh"
  }

  depends_on = [null_resource.run_terraform_in_pods]
}

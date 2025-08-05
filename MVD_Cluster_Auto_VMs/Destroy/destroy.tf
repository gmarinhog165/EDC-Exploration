# Define the list of IP addresses to connect to
variable "ssh_hosts" {
  type    = list(string)
  default = ["10.61.12.68", "10.61.12.45"]  # Replace with your IPs
}

variable "ssh_user" {
  type    = string
  default = "ubuntu"  # Replace with your SSH username
}

variable "ssh_private_key" {
  type    = string
  default = "~/.ssh/id_rsa"  # Replace with the path to your SSH private key
}

# Resource to run cleanup commands on remote hosts during destroy
resource "null_resource" "cleanup" {
  for_each = toset(var.ssh_hosts)  # Iterate over each IP address

  connection {
    type        = "ssh"
    host        = each.value  # Current IP address
    user        = var.ssh_user
    private_key = file(var.ssh_private_key)
  }

  provisioner "remote-exec" {

    inline = [
      "sudo kubeadm reset -f",
      "sudo rm -rf /etc/cni /etc/kubernetes /var/lib/dockershim /var/lib/etcd /var/lib/kubelet /var/run/kubernetes ~/.kube/*",
      "sudo iptables -F && sudo iptables -X",
      "sudo iptables -t nat -F && sudo iptables -t nat -X",
      "sudo iptables -t raw -F && sudo iptables -t raw -X",
      "sudo iptables -t mangle -F && sudo iptables -t mangle -X",
      "sudo systemctl restart docker",
    ]
  }
}

# Example resource to tie the cleanup to
resource "null_resource" "example" {
  # This is just a placeholder resource
  provisioner "local-exec" {
    command = "echo 'Creating resources...'"
  }

  # Ensure cleanup runs when this resource is destroyed
  depends_on = [null_resource.cleanup]
}

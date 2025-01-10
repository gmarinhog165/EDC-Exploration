# Minimum Viable Dataspace Demo


## 5. Running the Demo (Kubernetes)

For this section a basic understanding of Kubernetes, Docker, Gradle and Terraform is required. It is assumed that the
following tools are installed and readily available:

- Docker
- KinD (other cluster engines may work as well - not tested!)
- Terraform
- JDK 17+
- Git
- a POSIX compliant shell
- Postman (to comfortably execute REST requests)
- `openssl`, optional, but required to [regenerate keys](#91-regenerating-issuer-keys)
- `newman` (to run Postman collections from the command line)
- not needed, but recommended: Kubernetes monitoring tools like K9s

All commands are executed from the **repository's root folder** unless stated otherwise via `cd` commands.

> Since this is not a production deployment, all applications are deployed _in the same cluster_ and in the same
> namespace, plainly for the sake of simplicity.

### 5.1 Build the runtime images
Caso seja preciso gerar as imagens de novo para posteriormente adicionar ao Docker Hub:

```shell
./gradlew build
./gradlew -Ppersistence=true dockerize
```

this builds the runtime images and creates the following docker images: `controlplane:latest`, `dataplane:latest`,
`catalog-server:latest` and `identity-hub:latest` in the local docker image cache. Note the `-Ppersistence` flag which
puts the HashiCorp Vault module and PostgreSQL persistence modules on the runtime classpath.

> This demo will not work properly, if the `-Ppersistence=true` flag is omitted!

PostgreSQL and Hashicorp Vault obviously require additional configuration, which is handled by the Terraform scripts.

### 5.2 Create the K8S cluster

After the runtime images are built, we bring up and configure the Kubernetes cluster. We are using KinD here, but this
should work similarly well on other cluster runtimes, such as MicroK8s, K3s or Minikube. Please refer to the respective
documentation for more information.

```shell
minikube start --driver=docker --extra-config=kubelet.node-labels="ingress-ready=true" --ports=80:80 --ports=443:443

minikube addons enable ingress

# Deploy an NGINX ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for the ingress controller to become available
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Deploy the dataspace, type 'yes' when prompted
cd deployment
terraform init
terraform apply
```

Once Terraform has completed the deployment, type `kubectl get pods` and verify the output:

```shell
❯ kubectl get pods --namespace mvd
NAME                                                  READY   STATUS    RESTARTS   AGE
consumer-controlplane-5854f6f4d7-pk4lm                1/1     Running   0          24s
consumer-dataplane-64c59668fb-w66vz                   1/1     Running   0          17s
consumer-identityhub-57465876c5-9hdhj                 1/1     Running   0          24s
consumer-postgres-6978d86b59-8zbps                    1/1     Running   0          40s
consumer-vault-0                                      1/1     Running   0          37s
provider-catalog-server-7f78cf6875-bxc5p              1/1     Running   0          24s
provider-identityhub-f9d8d4446-nz7k7                  1/1     Running   0          24s
provider-manufacturing-controlplane-d74946b69-rdqnz   1/1     Running   0          24s
provider-manufacturing-dataplane-546956b4f8-hkx85     1/1     Running   0          17s
provider-postgres-75d64bb9fc-drf84                    1/1     Running   0          40s
provider-qna-controlplane-6cd65bf6f7-fpt7h            1/1     Running   0          24s
provider-qna-dataplane-5dc5fc4c7d-k4qh4               1/1     Running   0          17s
provider-vault-0                                      1/1     Running   0          36s
```

The consumer company has a controlplane, a dataplane, an IdentityHub, a postgres database and a vault to store secrets.
The provider company has a catalog server, a "provider-qna" and a "provider-manufacturing" controlplane/dataplane combo
plus an IdentityHub, a postgres database and a vault.

It is possible that pods need to restart a number of time before the cluster becomes stable. This is normal and
expected. If pods _don't_ come up after a reasonable amount of time, it is time to look at the logs and investigate.

Caso falte algum pod, isto falhou por motivos de tempo, basta fazer `terraform apply` de novo.

### 5.3 Seed the dataspace

Once all the deployments are up-and-running, the seed script needs to be executed which should produce command line
output similar to this:

```shell
./seed-k8s.sh


Seed data to "provider-qna" and "provider-manufacturing"
(node:545000) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)
(node:545154) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)


Create linked assets on the Catalog Server
(node:545270) [DEP0040] DeprecationWarning: The `punycode` module is deprecated. Please use a userland alternative instead.
(Use `node --trace-deprecation ...` to show where the warning was created)


Create consumer participant
ZGlkOndlYjphbGljZS1pZGVudGl0eWh1YiUzQTcwODM6YWxpY2U=.KPHR02XRnn+uT7vrpCIu8jJUADTBHKrterGq0PZTRJgzbzvgCXINcMWM3WBraG0aV/NxdJdl3RH3cqgyt+b5Lg==

Create provider participant
ZGlkOndlYjpib2ItaWRlbnRpdHlodWIlM0E3MDgzOmJvYg==.wBgVb44W6oi3lXlmeYsH6Xt3FAVO1g295W734jivUo5PKop6fpFsdXO4vC9D4I0WvqfB/cARJ+FVjjyFSIewew==%
```

_the `node` warnings are harmless and can be ignored_

> Failing to run the seed script will leave the dataspace in an uninitialized state and cause all connector-to-connector
> communication to fail.


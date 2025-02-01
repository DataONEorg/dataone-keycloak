# Keycloak Installation

Following instructions from Bitnami for their helm chart install.

## Info

- helm pull oci://registry-1.docker.io/bitnamicharts/keycloak
- helm install my-release oci://registry-1.docker.io/bitnamicharts/keycloak

## Testing install

```bash
k8 create -f storage-pvc.yaml
# Export three env vars below before running helm install
helm install -n keycloak keycloak oci://registry-1.docker.io/bitnamicharts/keycloak \
    --version 21.4.5 \
    --set auth.adminPassword=${KEYCLOAK_ADMIN_PASSWORD} \
    --set postgresql.postgresqlPassword=${POSTGRESQL_PASSWORD} \
    --set serviceAccount.create=false \
    -f dev-values.yaml
```

Output:
```txt
❯ helm install -n keycloak keycloak oci://registry-1.docker.io/bitnamicharts/keycloak \
>     --version 21.4.5 \
>     --set auth.adminPassword=${KEYCLOAK_ADMIN_PASSWORD} \
>     --set postgresql.postgresqlPassword=${POSTGRESQL_PASSWORD} \
>     --set serviceAccount.create=false \
>     -f dev-values.yaml
Pulled: registry-1.docker.io/bitnamicharts/keycloak:21.4.5
Digest: sha256:567ca7a6e52d27f82c0ff5064a77340be1f01eb0efbc2afaa055495441c0b030
NAME: keycloak
LAST DEPLOYED: Fri Jul  5 13:17:06 2024
NAMESPACE: keycloak
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
CHART NAME: keycloak
CHART VERSION: 21.4.5
APP VERSION: 24.0.5

** Please be patient while the chart is being deployed **

Keycloak can be accessed through the following DNS name from within your cluster:

    keycloak.keycloak.svc.cluster.local (port 80)

To access Keycloak from outside the cluster execute the following commands:

1. Get the Keycloak URL by running these commands:

    export HTTP_SERVICE_PORT=$(kubectl get --namespace keycloak -o jsonpath="{.spec.ports[?(@.name=='http')].port}" services keycloak)
    kubectl port-forward --namespace keycloak svc/keycloak ${HTTP_SERVICE_PORT}:${HTTP_SERVICE_PORT} &

    echo "http://127.0.0.1:${HTTP_SERVICE_PORT}/"

2. Access Keycloak using the obtained URL.
3. Access the Administration Console using the following credentials:

  echo Username: user
  echo Password: $(kubectl get secret --namespace keycloak keycloak -o jsonpath="{.data.admin-password}" | base64 -d)

WARNING: There are "resources" sections in the chart not set. Using "resourcesPreset" is not recommended for production. For production installations, please set the following values according to your workload needs:
  - resources
+info https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
```

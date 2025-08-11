## DataONE Keycloak Deployment

- **Authors**: Last, First (ORCID); ...
- **License**: [Apache 2](http://opensource.org/licenses/Apache-2.0)
- [Package source code on GitHub](https://github.com/DataONEorg/reponame)
- [**Submit Bugs and feature requests**](https://github.com/DataONEorg/reponame/issues)
- Contact us: support@dataone.org
- [DataONE discussions](https://github.com/DataONEorg/dataone/discussions)

This is an experimental repository to track deployment of the CNCF Keycloak platform as a potential
component within the DataONE authentication infrastructure.

Currently, we are following instructions from Bitnami for their helm chart install. 
Eventually, we would want to develop our own helm chart that likely depends on the 
Bitnami Keycloak as a subchart dependency.

DataONE in general is an open source, community project.  We [welcome contributions](./CONTRIBUTING.md) in many forms, including code, graphics, documentation, bug reports, testing, etc.  Use the [DataONE discussions](https://github.com/DataONEorg/dataone/discussions) to discuss these contributions with us.


## Documentation

Documentation is a work in progress, and can be found ...


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

## Adding ORCID provider

See: https://github.com/eosc-kc/keycloak-orcid

```
$ kubectl cp -n keycloak keycloak-orcid.jar keycloak-0:/opt/bitnami/keycloak/providers -c keycloak
# alternatively download with curl
# keycloak@keycloak-0:/opt/bitnami/keycloak/providers$ curl "https://github.com/eosc-kc/keycloak-orcid/releases/download/1.4.0/keycloak-orcid.jar" -o /opt/bitnami/keycloak/providers/keycloak-orcid.jar
# exec into container and rebuild
keycloak@keycloak-0:/opt/bitnami/keycloak/providers$ bash /opt/bitnami/keycloak/bin/kc.sh build
Appending additional Java properties to JAVA_OPTS
WARNING: The following run time options were found, but will be ignored during build time: kc.spi-admin-realm, kc.cache, kc.cache-stack, kc.db-url, kc.db-username, kc.db-password, kc.hostname, kc.hostname-strict, kc.http-enabled, kc.http-port, kc.https-port, kc.log-console-output, kc.log-level, kc.bootstrap-admin-username, kc.bootstrap-admin-password

Updating the configuration and installing your custom providers, if any. Please wait.
```

## Switching to Codecentric chart

The Codencentric helm chart uses the stock Keycloak image and deploys it as configured. It does not install it's own database, so one must provide a datatbase instance.

### Starting expermiment: use existing bitnami postgres as installed with codecentric keycloak

I updated the Codecentric values file in `values-kcx.yaml`, including setting `tag: 26.3.2` to use Keycloak 26.3.2. 

- Exec into bitnami postgres container, and using `psql -U postgres postgres` create a new `keycloak` database
  - `CREATE DATABASE keycloak WITH OWNER = bn_keycloak ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8';`
- Ensure the `keycloak-postgresql` secret is already loaded with a `password` key
- Ensure the `keycloak` secret is already loaded with a `admin-password` key
- Install / upgrade the codecentric chart using a values file that configures the DB parameters, as well as the ingress
  - Example in values-kcx.yaml
  - `helm upgrade keycloakx oci://ghcr.io/codecentric/helm-charts/keycloakx --version 7.0.1 -n keycloak --values values-kcx.yaml`
- The keycloak instance is now deployed at the ingress (e.g., https://auth.test.dataone.org/auth)

## Usage Example

To view more details about the Public API - see 'hashstore.py` interface documentation

```py
from product import Product

# Example code here...

```

## License
```
Copyright [2024] [Regents of the University of California]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Acknowledgements
Work on this package was supported by:

- DataONE Network
- Arctic Data Center: NSF-PLR grant #2042102 to M. B. Jones, A. Budden, M. Schildhauer, and J. Dozier

Additional support was provided for collaboration by the National Center for Ecological Analysis and Synthesis, a Center funded by the University of California, Santa Barbara, and the State of California.

[![DataONE_footer](https://user-images.githubusercontent.com/6643222/162324180-b5cf0f5f-ae7a-4ca6-87c3-9733a2590634.png)](https://dataone.org)

[![nceas_footer](https://www.nceas.ucsb.edu/sites/default/files/2020-03/NCEAS-full%20logo-4C.png)](https://www.nceas.ucsb.edu)

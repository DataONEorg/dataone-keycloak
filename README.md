## DataONE Keycloak Deployment

- **Authors**: Jones, Matthew B. (https://orcid.org/0000-0003-0077-4738);
- **License**: [Apache 2](http://opensource.org/licenses/Apache-2.0)
- [Package source code on GitHub](https://github.com/DataONEorg/dataone-keycloak)
- [**Submit Bugs and feature requests**](https://github.com/DataONEorg/dataone-keycloak/issues)
- Contact us: support@dataone.org
- [DataONE discussions](https://github.com/DataONEorg/dataone/discussions)

A helm chart for deploying the CNCF [Keycloak](https://www.keycloak.org/) platform as a component within the [DataONE](https://dataone.org) authentication infrastructure.

Keycloak provides OAuth2 and OIDC authentication services for applications. This chart is configured to provide
an OIDC endpoint for DataONE enabling client applications to log in and use authenticated credentials for accessing
DataONE services and member repositories.

DataONE in general is an open source, community project.  We [welcome contributions](./CONTRIBUTING.md) in many forms, including code, graphics, documentation, bug reports, testing, etc.  Use the [DataONE discussions](https://github.com/DataONEorg/dataone/discussions) to discuss these contributions with us.

## Install pre-requisite secrets and volumes

Create PVCs and secrets for keycloak and CloudNativePG.

```zsh
❯ kubectl apply -n keycloak -f admin/keycloak-cnpg-secret.yaml
secret/keycloak-pg created
❯ kubectl apply -n keycloak -f admin/keycloak-secret-prod.yaml
secret/keycloak created
❯ kubectl apply -n keycloak -f admin/kc-vault-secret-prod.yaml
secret/kc-vault created
```

## Install Provider credentials as mountable secret

When keycloak is authenticating with LDAP for user federation and with providers like ORCID as IdPs, it needs authentication credentials. Keycloak provides a vault feature that supports looking up these credentials from SPI-compliant vault providers, including from plain text files that are mounted in the container. This is useful in kubernetes where the credentials can be added to secrets and then mounted in the container at a known filepath. We configure keystore to use vault credentials mounted from a secret named `kc-vault` for both:

- DataONE LDAP user-federation (use ${vault.ldap} as the config key)
- DataONE ORCID provider (use ${vault.orcid} as the config key)

Within the Keycloak vault, requests for these vault secrets get mapped to requests for mounted files with the naming pattern `realm_key`, where `realm` is the Keycloak realm for the provider (typically `dataone` for us), and `key` is the name of the provider key we used to create the secret. To deploy in our typical configuration for DataONE, you should create a secret with two keys, one named `dataone_ldap` and one named `dataone_orcid`. Each secret should contain the password value for that provider.  When configuring the `dataone` realm, we then use `${vault.ldap}` to represent the LDAP password, and `${vault.orcid}` to represent the ORCID provider password. You can create the necessary secret with a command such as:

```
❯ kubectl create secret generic -n keycloak kc-vault --from-file=dataone_ldap=./admin/ldap.txt --from-file=dataone_orcid=./admin/orcid.txt
secret/kc-vault created
```

## Install the dataone-keycloak helm chart

Make sure you're in the correct k8s context, then:

```txt
❯ helm upgrade --install keycloakx -n keycloak -f values.yaml \
       oci://ghcr.io/dataone/charts/dataone-keycloak --version [version]
Release "keycloakx" has been upgraded. Happy Helming!
NAME: keycloakx
LAST DEPLOYED: Mon Sep 15 14:39:24 2025
NAMESPACE: keycloak
STATUS: deployed
REVISION: 11
TEST SUITE: None
NOTES:
1. Get the application URL by running these commands:
```

## Adding ORCID provider

DataONE uses [orcid.org](https://orcid.org) as an identity provider for common subject identifiers for people across the repository network for both authentication and access control purposes. This chart installs the [EOSC keycloak-orcid](https://github.com/eosc-kc/keycloak-orcid) provider plugin to enable login via ORCID identitities. 

## Building the `keycloak-init` image

This deployment depends on a `ghcr.io/dataoneorg/keycloak-init` image which is used in an init container to provisions providers, themes, and validates dependencies before the main keycloak container starts. This `keycloak-init` image is based on Alpine, and contains key configuration files that are used in keycloak, including the ORCID provisioner providing ORCID logins, and our customized `dataone` theme for keycloak. The image must be rebuilt and pushed to ghcr.io any time that changes to the ORCID provider or the dataone theme have occurred. 

Multi-platform builds can be supported using `docker buildx`. First you have to create a builder targeting the patforms of choice, and then you can use it to build an image for those architectures. Here's an example showing a build for arm64 and amd64, and pushing the resulting image to GHCR (you need to be logged in first with a GITHUB PAT):

```sh
echo $GITHUB_PAT | docker login ghcr.io -u mbjones --password-stdin

docker buildx create --use --platform=linux/arm64,linux/amd64 --name multi-platform-builder
docker buildx inspect --bootstrap

docker buildx build --platform linux/arm64/v8,linux/amd64 --push -t ghcr.io/dataoneorg/keycloak-init:0.1.0 .
```

## Switching to Codecentric chart

This chart depends on the Codecentric helm chart, which in turn uses the stock Keycloak image and deploys it as configured. It does not install its own database, so one must provide a database instance and configure the chart to point at it.

## Setting up CloudNativePG postgres database

The helm chart creates a CloudNativePG postgres cluster with one read-write node and two read-only replica nodes.

After a few minutes from chart creation, CNPG will spin up the postgres replicas, and you can view the status of the cluster using the `kubectl cnpg` plugin:

```
❯ kubectl cnpg status keycloak-pg -n keycloak
Cluster Summary
Name                 keycloak/keycloak-pg
System ID:           7538165093337247771
PostgreSQL Image:    ghcr.io/cloudnative-pg/postgresql:17.5
Primary instance:    keycloak-cnpg-1
Primary start time:  2025-08-13 20:10:44 +0000 UTC (uptime 1m28s)
Status:              Cluster in healthy state
Instances:           3
Ready instances:     3
Size:                126M
Current Write LSN:   0/6000060 (Timeline: 1 - WAL File: 000000010000000000000006)

Continuous Backup status
Not configured

Streaming Replication status
Replication Slots Enabled
Name             Sent LSN   Write LSN  Flush LSN  Replay LSN  Write Lag  Flush Lag  Replay Lag  State      Sync State  Sync Priority  Replication Slot
----             --------   ---------  ---------  ----------  ---------  ---------  ----------  -----      ----------  -------------  ----------------
keycloak-cnpg-2  0/6000060  0/6000060  0/6000060  0/6000060   00:00:00   00:00:00   00:00:00    streaming  async       0              active
keycloak-cnpg-3  0/6000060  0/6000060  0/6000060  0/6000060   00:00:00   00:00:00   00:00:00    streaming  async       0              active

Instances status
Name             Current LSN  Replication role  Status  QoS         Manager Version  Node
----             -----------  ----------------  ------  ---         ---------------  ----
keycloak-cnpg-1  0/6000060    Primary           OK      BestEffort  1.27.0           k8s-dev-node-3
keycloak-cnpg-2  0/6000060    Standby (async)   OK      BestEffort  1.27.0           k8s-dev-node-1
keycloak-cnpg-3  0/6000060    Standby (async)   OK      BestEffort  1.27.0           k8s-dev-node-2
```

Now there are three keycloak Postgres replicas up and running. THe primary `keycloak-pg-rw` should be used for read-write operations, and the other replicas (`keycloak-pg-ro`, `keycloak-pg-r`) can be used for read queries and will help scale the application. Under heavy loads, in theory we can create more replicas with `kubectl scale` to serve higher read-only query loads, but keycloak generally requires a write connection. Therefore, these replic nodes really represent hot-backups that could be promoted to the primary read-write node if needed to keep the cluster operational.
```
❯ kubectl -n keycloak get services
NAME                       TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                    AGE
keycloak-cnpg-r            ClusterIP   10.111.28.124    <none>        5432/TCP                   3m43s
keycloak-cnpg-ro           ClusterIP   10.110.90.138    <none>        5432/TCP                   3m43s
keycloak-cnpg-rw           ClusterIP   10.109.57.188    <none>        5432/TCP                   3m43s
keycloakx-headless         ClusterIP   None             <none>        80/TCP                     4d23h
keycloakx-http             ClusterIP   10.101.226.135   <none>        9000/TCP,80/TCP,8443/TCP   4d23h
```

## Parameters

### Global Properties Shared Across Sub-Charts Within This Deployment

| Name                         | Description                                          | Value                     |
| ---------------------------- | ---------------------------------------------------- | ------------------------- |
| `global.defaultStorageClass` | Global default StorageClass for Persistent Volume(s) | `csi-cephfs-sc-ephemeral` |

### Keycloak Configuration

| Name                                                                                | Description                                                                      | Value                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `keycloakx.replicas`                                                                | The number of keycloak replicas to create (has no effect if autoscaling enabled) | `1`                                                                                                                                                                                                                                                                                                                                                                                                  |
| `keycloakx.serviceAccount.create`                                                   | Specifies whether a ServiceAccount should be created                             | `false`                                                                                                                                                                                                                                                                                                                                                                                              |
| `keycloakx.extraInitContainers`                                                     | Additional init containers, e. g. for providing custom themes and providers      | `- name: providers-init`                           |
| `keycloakx.command`                                                                 | Overrides the default entrypoint of the Keycloak container                       | `["/opt/keycloak/bin/kc.sh","--verbose","start","--http-port=8080","--hostname-strict=false","--spi-events-listener-jboss-logging-success-level=info","--spi-events-listener-jboss-logging-error-level=warn","--spi-theme--static-max-age=-1","--spi-theme--cache-themes=false","--spi-theme--cache-templates=false","--log-level=error","--log-level-org.keycloak.social.user_profile_dump=debug"]` |
| `keycloakx.extraEnv`                                                                | Additional environment variables for Keycloak                                    | |
| `keycloakx.extraVolumes`                                                            | Add additional volumes, e. g. for custom themes and providers                    | `- name: providers`                                                                                                                                                                                                                                                                                        |
| `keycloakx.extraVolumeMounts`                                                       | Add additional volumes mounts, e. g. for custom themes and providers             |                                                                                                                                                                                                                                                                                         |
| `keycloakx.ingress.enabled`                                                         | If `true`, an Ingress is created                                                 | `true`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.ingress.ingressClassName`                                                | The name of the Ingress Class associated with this ingress                       | `nginx`                                                                                                                                                                                                                                                                                                                                                                                              |
| `keycloakx.ingress.servicePort`                                                     | The Service port targeted by the Ingress                                         | `http`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.ingress.annotations.nginx.ingress.kubernetes.io/proxy-buffer-size`       | Default proxy buffer size                                                        | `128k`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.ingress.annotations.nginx.ingress.kubernetes.io/client-body-buffer-size` | Default client bidy buffer size                                                  | `1m`                                                                                                                                                                                                                                                                                                                                                                                                 |
| `keycloakx.ingress.annotations.nginx.ingress.kubernetes.io/client_max_body_size`    | Maximum client body size                                                         | `10m`                                                                                                                                                                                                                                                                                                                                                                                                |
| `keycloakx.ingress.annotations.cert-manager.io/cluster-issuer`                      | Name of the cluster cert issuer for Let's Encrypt                                | `letsencrypt-prod`                                                                                                                                                                                                                                                                                                                                                                                   |
| `keycloakx.ingress.rules[0].host`                                                   | Ingress hostname for the keycloak service                                        | `auth.test.dataone.org`                                                                                                                                                                                                                                                                                                                                                                              |
| `keycloakx.ingress.rules[0].paths[0].path`                                          | Ingress path for the keycloak service                                            | `{{ tpl .Values.http.relativePath $ | trimSuffix "/" }}/`                                                                                                                                                                                                                                                                                                                                            |
| `keycloakx.ingress.rules[0].paths[0].pathType`                                      | Ingress pathType for the keycloak service                                        | `Prefix`                                                                                                                                                                                                                                                                                                                                                                                             |
| `keycloakx.ingress.tls[0].hosts`                                                    | TLS hostname for the keycloak service                                            | `["auth.test.dataone.org"]`                                                                                                                                                                                                                                                                                                                                                                          |
| `keycloakx.ingress.tls[0].secretName`                                               | TLS secret name for the keycloak service                                         | `ingress-nginx-tls-cert`                                                                                                                                                                                                                                                                                                                                                                             |
| `keycloakx.database.database`                                                       | The name of the database used by the keycloak service.                           | `keycloak`                                                                                                                                                                                                                                                                                                                                                                                           |
| `keycloakx.database.replicas`                                                       | The number of database replicas used by the keycloak service.                    | `3`                                                                                                                                                                                                                                                                                                                                                                                                  |
| `keycloakx.database.storageClass`                                                   | The storageClass to be used by CloudNativePG to create storage volumes.          | `csi-cephfs-sc-ephemeral`                                                                                                                                                                                                                                                                                                                                                                            |
| `keycloakx.database.size`                                                           | The size to be used by CloudNativePG to create storage volumes.                  | `10Gi`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.database.username`                                                       | Name of the application database owner and user for keycloak                     | `keycloak`                                                                                                                                                                                                                                                                                                                                                                                           |
| `keycloakx.database.existingSecret`                                                 | Secret to be used for postgres password                                          | `keycloak-pg`                                                                                                                                                                                                                                                                                                                                                                                        |
| `keycloakx.database.existingSecretKey`                                              | name of the key in the existingSecret containing the password field              | `password`                                                                                                                                                                                                                                                                                                                                                                                           |
| `keycloakx.database.vendor`                                                         | name of the database vendor, only `postgres` supported in Keycloak now           | `postgres`                                                                                                                                                                                                                                                                                                                                                                                           |
| `keycloakx.database.hostname`                                                       | the hostname of the database service.                                            | `keycloakx-cnpg-rw`                                                                                                                                                                                                                                                                                                                                                                                  |
| `keycloakx.database.port`                                                           | the port used for connecting to the database                                     | `5432`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.proxy.enabled`                                                           | true if keycloak is installed behind a proxy like a k8s Ingress                  | `true`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.proxy.mode`                                                              | set to `xforwarded` if X-Forwarded` headers are set by the proxy                 | `xforwarded`                                                                                                                                                                                                                                                                                                                                                                                         |
| `keycloakx.proxy.http.enabled`                                                      | true if keycloak is proxy uses http                                              | `true`                                                                                                                                                                                                                                                                                                                                                                                               |
| `keycloakx.http.relativePath`                                                       | The path at which the ingress will respond, typically `/auth`                    | `/auth`                                                                                                                                                                                                                                                                                                                                                                                              |

## License
```
Copyright [2025] [Regents of the University of California]

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

- [DataONE](https://dataone.org)
- Arctic Data Center: NSF-PLR grant #2042102 to M. B. Jones, A. Budden, M. Schildhauer, and J. Dozier

Additional support was provided for collaboration by the National Center for Ecological Analysis and Synthesis, a Center funded by the University of California, Santa Barbara, and the State of California.

[![DataONE_footer](https://user-images.githubusercontent.com/6643222/162324180-b5cf0f5f-ae7a-4ca6-87c3-9733a2590634.png)](https://dataone.org)

[![nceas_footer](https://www.nceas.ucsb.edu/sites/default/files/2020-03/NCEAS-full%20logo-4C.png)](https://www.nceas.ucsb.edu)

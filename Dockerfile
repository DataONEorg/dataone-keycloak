FROM alpine:latest
LABEL org.opencontainers.image.source="https://github.com/dataoneorg/dataone-keycloak"
LABEL org.opencontainers.image.title="DataONE Keycloak config init container"
LABEL org.opencontainers.image.version="0.1.0"
COPY themes /themes
RUN mkdir -p /providers
RUN wget -O "/providers/keycloak-orcid-1.5.0.jar" "https://github.com/eosc-kc/keycloak-orcid/releases/download/1.5.0/keycloak-orcid.jar"

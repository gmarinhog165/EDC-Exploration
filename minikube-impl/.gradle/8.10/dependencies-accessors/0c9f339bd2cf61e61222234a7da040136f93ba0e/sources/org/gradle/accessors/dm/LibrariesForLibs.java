package org.gradle.accessors.dm;

import org.gradle.api.NonNullApi;
import org.gradle.api.artifacts.MinimalExternalModuleDependency;
import org.gradle.plugin.use.PluginDependency;
import org.gradle.api.artifacts.ExternalModuleDependencyBundle;
import org.gradle.api.artifacts.MutableVersionConstraint;
import org.gradle.api.provider.Provider;
import org.gradle.api.model.ObjectFactory;
import org.gradle.api.provider.ProviderFactory;
import org.gradle.api.internal.catalog.AbstractExternalDependencyFactory;
import org.gradle.api.internal.catalog.DefaultVersionCatalog;
import java.util.Map;
import org.gradle.api.internal.attributes.ImmutableAttributesFactory;
import org.gradle.api.internal.artifacts.dsl.CapabilityNotationParser;
import javax.inject.Inject;

/**
 * A catalog of dependencies accessible via the {@code libs} extension.
 */
@NonNullApi
public class LibrariesForLibs extends AbstractExternalDependencyFactory {

    private final AbstractExternalDependencyFactory owner = this;
    private final EdcLibraryAccessors laccForEdcLibraryAccessors = new EdcLibraryAccessors(owner);
    private final JacksonLibraryAccessors laccForJacksonLibraryAccessors = new JacksonLibraryAccessors(owner);
    private final JakartaLibraryAccessors laccForJakartaLibraryAccessors = new JakartaLibraryAccessors(owner);
    private final VersionAccessors vaccForVersionAccessors = new VersionAccessors(providers, config);
    private final BundleAccessors baccForBundleAccessors = new BundleAccessors(objects, providers, config, attributesFactory, capabilityNotationParser);
    private final PluginAccessors paccForPluginAccessors = new PluginAccessors(providers, config);

    @Inject
    public LibrariesForLibs(DefaultVersionCatalog config, ProviderFactory providers, ObjectFactory objects, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) {
        super(config, providers, objects, attributesFactory, capabilityNotationParser);
    }

    /**
     * Dependency provider for <b>awaitility</b> with <b>org.awaitility:awaitility</b> coordinates and
     * with version reference <b>awaitility</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getAwaitility() {
        return create("awaitility");
    }

    /**
     * Dependency provider for <b>parsson</b> with <b>org.eclipse.parsson:parsson</b> coordinates and
     * with version reference <b>parsson</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getParsson() {
        return create("parsson");
    }

    /**
     * Dependency provider for <b>postgres</b> with <b>org.postgresql:postgresql</b> coordinates and
     * with version reference <b>postgres</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getPostgres() {
        return create("postgres");
    }

    /**
     * Dependency provider for <b>restAssured</b> with <b>io.rest-assured:rest-assured</b> coordinates and
     * with version reference <b>restAssured</b>
     * <p>
     * This dependency was declared in catalog libs.versions.toml
     */
    public Provider<MinimalExternalModuleDependency> getRestAssured() {
        return create("restAssured");
    }

    /**
     * Group of libraries at <b>edc</b>
     */
    public EdcLibraryAccessors getEdc() {
        return laccForEdcLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jackson</b>
     */
    public JacksonLibraryAccessors getJackson() {
        return laccForJacksonLibraryAccessors;
    }

    /**
     * Group of libraries at <b>jakarta</b>
     */
    public JakartaLibraryAccessors getJakarta() {
        return laccForJakartaLibraryAccessors;
    }

    /**
     * Group of versions at <b>versions</b>
     */
    public VersionAccessors getVersions() {
        return vaccForVersionAccessors;
    }

    /**
     * Group of bundles at <b>bundles</b>
     */
    public BundleAccessors getBundles() {
        return baccForBundleAccessors;
    }

    /**
     * Group of plugins at <b>plugins</b>
     */
    public PluginAccessors getPlugins() {
        return paccForPluginAccessors;
    }

    public static class EdcLibraryAccessors extends SubDependencyFactory {
        private final EdcApiLibraryAccessors laccForEdcApiLibraryAccessors = new EdcApiLibraryAccessors(owner);
        private final EdcBomLibraryAccessors laccForEdcBomLibraryAccessors = new EdcBomLibraryAccessors(owner);
        private final EdcControlplaneLibraryAccessors laccForEdcControlplaneLibraryAccessors = new EdcControlplaneLibraryAccessors(owner);
        private final EdcCoreLibraryAccessors laccForEdcCoreLibraryAccessors = new EdcCoreLibraryAccessors(owner);
        private final EdcDcpLibraryAccessors laccForEdcDcpLibraryAccessors = new EdcDcpLibraryAccessors(owner);
        private final EdcDidLibraryAccessors laccForEdcDidLibraryAccessors = new EdcDidLibraryAccessors(owner);
        private final EdcExtLibraryAccessors laccForEdcExtLibraryAccessors = new EdcExtLibraryAccessors(owner);
        private final EdcFcLibraryAccessors laccForEdcFcLibraryAccessors = new EdcFcLibraryAccessors(owner);
        private final EdcIhLibraryAccessors laccForEdcIhLibraryAccessors = new EdcIhLibraryAccessors(owner);
        private final EdcLibLibraryAccessors laccForEdcLibLibraryAccessors = new EdcLibLibraryAccessors(owner);
        private final EdcOauth2LibraryAccessors laccForEdcOauth2LibraryAccessors = new EdcOauth2LibraryAccessors(owner);
        private final EdcSpiLibraryAccessors laccForEdcSpiLibraryAccessors = new EdcSpiLibraryAccessors(owner);
        private final EdcSqlLibraryAccessors laccForEdcSqlLibraryAccessors = new EdcSqlLibraryAccessors(owner);
        private final EdcStsLibraryAccessors laccForEdcStsLibraryAccessors = new EdcStsLibraryAccessors(owner);
        private final EdcVaultLibraryAccessors laccForEdcVaultLibraryAccessors = new EdcVaultLibraryAccessors(owner);

        public EdcLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>boot</b> with <b>org.eclipse.edc:boot</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getBoot() {
            return create("edc.boot");
        }

        /**
         * Dependency provider for <b>dsp</b> with <b>org.eclipse.edc:dsp</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDsp() {
            return create("edc.dsp");
        }

        /**
         * Dependency provider for <b>junit</b> with <b>org.eclipse.edc:junit</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJunit() {
            return create("edc.junit");
        }

        /**
         * Group of libraries at <b>edc.api</b>
         */
        public EdcApiLibraryAccessors getApi() {
            return laccForEdcApiLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.bom</b>
         */
        public EdcBomLibraryAccessors getBom() {
            return laccForEdcBomLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.controlplane</b>
         */
        public EdcControlplaneLibraryAccessors getControlplane() {
            return laccForEdcControlplaneLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.core</b>
         */
        public EdcCoreLibraryAccessors getCore() {
            return laccForEdcCoreLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.dcp</b>
         */
        public EdcDcpLibraryAccessors getDcp() {
            return laccForEdcDcpLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.did</b>
         */
        public EdcDidLibraryAccessors getDid() {
            return laccForEdcDidLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.ext</b>
         */
        public EdcExtLibraryAccessors getExt() {
            return laccForEdcExtLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.fc</b>
         */
        public EdcFcLibraryAccessors getFc() {
            return laccForEdcFcLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.ih</b>
         */
        public EdcIhLibraryAccessors getIh() {
            return laccForEdcIhLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.lib</b>
         */
        public EdcLibLibraryAccessors getLib() {
            return laccForEdcLibLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.oauth2</b>
         */
        public EdcOauth2LibraryAccessors getOauth2() {
            return laccForEdcOauth2LibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.spi</b>
         */
        public EdcSpiLibraryAccessors getSpi() {
            return laccForEdcSpiLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sql</b>
         */
        public EdcSqlLibraryAccessors getSql() {
            return laccForEdcSqlLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sts</b>
         */
        public EdcStsLibraryAccessors getSts() {
            return laccForEdcStsLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.vault</b>
         */
        public EdcVaultLibraryAccessors getVault() {
            return laccForEdcVaultLibraryAccessors;
        }

    }

    public static class EdcApiLibraryAccessors extends SubDependencyFactory {
        private final EdcApiDspLibraryAccessors laccForEdcApiDspLibraryAccessors = new EdcApiDspLibraryAccessors(owner);
        private final EdcApiManagementLibraryAccessors laccForEdcApiManagementLibraryAccessors = new EdcApiManagementLibraryAccessors(owner);

        public EdcApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>observability</b> with <b>org.eclipse.edc:api-observability</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getObservability() {
            return create("edc.api.observability");
        }

        /**
         * Dependency provider for <b>version</b> with <b>org.eclipse.edc:version-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getVersion() {
            return create("edc.api.version");
        }

        /**
         * Group of libraries at <b>edc.api.dsp</b>
         */
        public EdcApiDspLibraryAccessors getDsp() {
            return laccForEdcApiDspLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.api.management</b>
         */
        public EdcApiManagementLibraryAccessors getManagement() {
            return laccForEdcApiManagementLibraryAccessors;
        }

    }

    public static class EdcApiDspLibraryAccessors extends SubDependencyFactory {

        public EdcApiDspLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>config</b> with <b>org.eclipse.edc:dsp-http-api-configuration</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getConfig() {
            return create("edc.api.dsp.config");
        }

    }

    public static class EdcApiManagementLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcApiManagementLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>management</b> with <b>org.eclipse.edc:management-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.api.management");
        }

        /**
         * Dependency provider for <b>config</b> with <b>org.eclipse.edc:management-api-configuration</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getConfig() {
            return create("edc.api.management.config");
        }

    }

    public static class EdcBomLibraryAccessors extends SubDependencyFactory {
        private final EdcBomControlplaneLibraryAccessors laccForEdcBomControlplaneLibraryAccessors = new EdcBomControlplaneLibraryAccessors(owner);
        private final EdcBomDataplaneLibraryAccessors laccForEdcBomDataplaneLibraryAccessors = new EdcBomDataplaneLibraryAccessors(owner);
        private final EdcBomIdentithubLibraryAccessors laccForEdcBomIdentithubLibraryAccessors = new EdcBomIdentithubLibraryAccessors(owner);

        public EdcBomLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.bom.controlplane</b>
         */
        public EdcBomControlplaneLibraryAccessors getControlplane() {
            return laccForEdcBomControlplaneLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.bom.dataplane</b>
         */
        public EdcBomDataplaneLibraryAccessors getDataplane() {
            return laccForEdcBomDataplaneLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.bom.identithub</b>
         */
        public EdcBomIdentithubLibraryAccessors getIdentithub() {
            return laccForEdcBomIdentithubLibraryAccessors;
        }

    }

    public static class EdcBomControlplaneLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcBomControlplaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>controlplane</b> with <b>org.eclipse.edc:controlplane-dcp-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.bom.controlplane");
        }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:controlplane-feature-sql-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.bom.controlplane.sql");
        }

    }

    public static class EdcBomDataplaneLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcBomDataplaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dataplane</b> with <b>org.eclipse.edc:dataplane-base-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.bom.dataplane");
        }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:dataplane-feature-sql-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.bom.dataplane.sql");
        }

    }

    public static class EdcBomIdentithubLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcBomIdentithubLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>identithub</b> with <b>org.eclipse.edc:identityhub-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.bom.identithub");
        }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:identityhub-feature-sql-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.bom.identithub.sql");
        }

        /**
         * Dependency provider for <b>sts</b> with <b>org.eclipse.edc:identityhub-with-sts-bom</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSts() {
            return create("edc.bom.identithub.sts");
        }

    }

    public static class EdcControlplaneLibraryAccessors extends SubDependencyFactory {

        public EdcControlplaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:control-plane-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.controlplane.core");
        }

        /**
         * Dependency provider for <b>services</b> with <b>org.eclipse.edc:control-plane-aggregate-services</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getServices() {
            return create("edc.controlplane.services");
        }

        /**
         * Dependency provider for <b>transform</b> with <b>org.eclipse.edc:control-plane-transform</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTransform() {
            return create("edc.controlplane.transform");
        }

    }

    public static class EdcCoreLibraryAccessors extends SubDependencyFactory {

        public EdcCoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>connector</b> with <b>org.eclipse.edc:connector-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getConnector() {
            return create("edc.core.connector");
        }

        /**
         * Dependency provider for <b>edrstore</b> with <b>org.eclipse.edc:edr-store-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getEdrstore() {
            return create("edc.core.edrstore");
        }

        /**
         * Dependency provider for <b>token</b> with <b>org.eclipse.edc:token-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getToken() {
            return create("edc.core.token");
        }

    }

    public static class EdcDcpLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcDcpLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>dcp</b> with <b>org.eclipse.edc:identity-trust-service</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.dcp");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:identity-trust-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.dcp.core");
        }

    }

    public static class EdcDidLibraryAccessors extends SubDependencyFactory {

        public EdcDidLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:identity-did-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.did.core");
        }

        /**
         * Dependency provider for <b>web</b> with <b>org.eclipse.edc:identity-did-web</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getWeb() {
            return create("edc.did.web");
        }

    }

    public static class EdcExtLibraryAccessors extends SubDependencyFactory {

        public EdcExtLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>http</b> with <b>org.eclipse.edc:http</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getHttp() {
            return create("edc.ext.http");
        }

        /**
         * Dependency provider for <b>jsonld</b> with <b>org.eclipse.edc:json-ld</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJsonld() {
            return create("edc.ext.jsonld");
        }

    }

    public static class EdcFcLibraryAccessors extends SubDependencyFactory {
        private final EdcFcSpiLibraryAccessors laccForEdcFcSpiLibraryAccessors = new EdcFcSpiLibraryAccessors(owner);

        public EdcFcLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:federated-catalog-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("edc.fc.api");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:federated-catalog-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.fc.core");
        }

        /**
         * Group of libraries at <b>edc.fc.spi</b>
         */
        public EdcFcSpiLibraryAccessors getSpi() {
            return laccForEdcFcSpiLibraryAccessors;
        }

    }

    public static class EdcFcSpiLibraryAccessors extends SubDependencyFactory {

        public EdcFcSpiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>crawler</b> with <b>org.eclipse.edc:crawler-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCrawler() {
            return create("edc.fc.spi.crawler");
        }

    }

    public static class EdcIhLibraryAccessors extends SubDependencyFactory {
        private final EdcIhLibLibraryAccessors laccForEdcIhLibLibraryAccessors = new EdcIhLibLibraryAccessors(owner);
        private final EdcIhSpiLibraryAccessors laccForEdcIhSpiLibraryAccessors = new EdcIhSpiLibraryAccessors(owner);

        public EdcIhLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.ih.lib</b>
         */
        public EdcIhLibLibraryAccessors getLib() {
            return laccForEdcIhLibLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.ih.spi</b>
         */
        public EdcIhSpiLibraryAccessors getSpi() {
            return laccForEdcIhSpiLibraryAccessors;
        }

    }

    public static class EdcIhLibLibraryAccessors extends SubDependencyFactory {

        public EdcIhLibLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>credentialquery</b> with <b>org.eclipse.edc:credential-query-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCredentialquery() {
            return create("edc.ih.lib.credentialquery");
        }

    }

    public static class EdcIhSpiLibraryAccessors extends SubDependencyFactory {

        public EdcIhSpiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>did</b> with <b>org.eclipse.edc:did-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDid() {
            return create("edc.ih.spi.did");
        }

        /**
         * Dependency provider for <b>store</b> with <b>org.eclipse.edc:identity-hub-store-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getStore() {
            return create("edc.ih.spi.store");
        }

    }

    public static class EdcLibLibraryAccessors extends SubDependencyFactory {

        public EdcLibLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>crypto</b> with <b>org.eclipse.edc:crypto-common-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCrypto() {
            return create("edc.lib.crypto");
        }

        /**
         * Dependency provider for <b>jsonld</b> with <b>org.eclipse.edc:json-ld-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJsonld() {
            return create("edc.lib.jsonld");
        }

        /**
         * Dependency provider for <b>jws2020</b> with <b>org.eclipse.edc:jws2020-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJws2020() {
            return create("edc.lib.jws2020");
        }

        /**
         * Dependency provider for <b>keys</b> with <b>org.eclipse.edc:keys-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getKeys() {
            return create("edc.lib.keys");
        }

        /**
         * Dependency provider for <b>transform</b> with <b>org.eclipse.edc:transform-lib</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTransform() {
            return create("edc.lib.transform");
        }

    }

    public static class EdcOauth2LibraryAccessors extends SubDependencyFactory {

        public EdcOauth2LibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:oauth2-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getClient() {
            return create("edc.oauth2.client");
        }

    }

    public static class EdcSpiLibraryAccessors extends SubDependencyFactory {
        private final EdcSpiIdentityLibraryAccessors laccForEdcSpiIdentityLibraryAccessors = new EdcSpiIdentityLibraryAccessors(owner);

        public EdcSpiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>catalog</b> with <b>org.eclipse.edc:catalog-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCatalog() {
            return create("edc.spi.catalog");
        }

        /**
         * Dependency provider for <b>transform</b> with <b>org.eclipse.edc:transform-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTransform() {
            return create("edc.spi.transform");
        }

        /**
         * Group of libraries at <b>edc.spi.identity</b>
         */
        public EdcSpiIdentityLibraryAccessors getIdentity() {
            return laccForEdcSpiIdentityLibraryAccessors;
        }

    }

    public static class EdcSpiIdentityLibraryAccessors extends SubDependencyFactory {

        public EdcSpiIdentityLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>did</b> with <b>org.eclipse.edc:identity-did-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getDid() {
            return create("edc.spi.identity.did");
        }

        /**
         * Dependency provider for <b>trust</b> with <b>org.eclipse.edc:identity-trust-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTrust() {
            return create("edc.spi.identity.trust");
        }

    }

    public static class EdcSqlLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlDataplaneLibraryAccessors laccForEdcSqlDataplaneLibraryAccessors = new EdcSqlDataplaneLibraryAccessors(owner);
        private final EdcSqlIhLibraryAccessors laccForEdcSqlIhLibraryAccessors = new EdcSqlIhLibraryAccessors(owner);

        public EdcSqlLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>assetindex</b> with <b>org.eclipse.edc:asset-index-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getAssetindex() {
            return create("edc.sql.assetindex");
        }

        /**
         * Dependency provider for <b>contractdef</b> with <b>org.eclipse.edc:contract-definition-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getContractdef() {
            return create("edc.sql.contractdef");
        }

        /**
         * Dependency provider for <b>contractneg</b> with <b>org.eclipse.edc:contract-negotiation-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getContractneg() {
            return create("edc.sql.contractneg");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:sql-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.sql.core");
        }

        /**
         * Dependency provider for <b>edrcache</b> with <b>org.eclipse.edc:edr-index-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getEdrcache() {
            return create("edc.sql.edrcache");
        }

        /**
         * Dependency provider for <b>jtivdalidation</b> with <b>org.eclipse.edc:jti-validation-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJtivdalidation() {
            return create("edc.sql.jtivdalidation");
        }

        /**
         * Dependency provider for <b>lease</b> with <b>org.eclipse.edc:sql-lease</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getLease() {
            return create("edc.sql.lease");
        }

        /**
         * Dependency provider for <b>policydef</b> with <b>org.eclipse.edc:policy-definition-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getPolicydef() {
            return create("edc.sql.policydef");
        }

        /**
         * Dependency provider for <b>pool</b> with <b>org.eclipse.edc:sql-pool-apache-commons</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getPool() {
            return create("edc.sql.pool");
        }

        /**
         * Dependency provider for <b>transactionlocal</b> with <b>org.eclipse.edc:transaction-local</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTransactionlocal() {
            return create("edc.sql.transactionlocal");
        }

        /**
         * Dependency provider for <b>transferprocess</b> with <b>org.eclipse.edc:transfer-process-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getTransferprocess() {
            return create("edc.sql.transferprocess");
        }

        /**
         * Group of libraries at <b>edc.sql.dataplane</b>
         */
        public EdcSqlDataplaneLibraryAccessors getDataplane() {
            return laccForEdcSqlDataplaneLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sql.ih</b>
         */
        public EdcSqlIhLibraryAccessors getIh() {
            return laccForEdcSqlIhLibraryAccessors;
        }

    }

    public static class EdcSqlDataplaneLibraryAccessors extends SubDependencyFactory {

        public EdcSqlDataplaneLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>instancestore</b> with <b>org.eclipse.edc:data-plane-instance-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getInstancestore() {
            return create("edc.sql.dataplane.instancestore");
        }

    }

    public static class EdcSqlIhLibraryAccessors extends SubDependencyFactory {
        private final EdcSqlIhStsstoreLibraryAccessors laccForEdcSqlIhStsstoreLibraryAccessors = new EdcSqlIhStsstoreLibraryAccessors(owner);

        public EdcSqlIhLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>edc.sql.ih.stsstore</b>
         */
        public EdcSqlIhStsstoreLibraryAccessors getStsstore() {
            return laccForEdcSqlIhStsstoreLibraryAccessors;
        }

    }

    public static class EdcSqlIhStsstoreLibraryAccessors extends SubDependencyFactory {

        public EdcSqlIhStsstoreLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>sql</b> with <b>org.eclipse.edc:sts-client-store-sql</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSql() {
            return create("edc.sql.ih.stsstore.sql");
        }

    }

    public static class EdcStsLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {
        private final EdcStsAccountserviceLibraryAccessors laccForEdcStsAccountserviceLibraryAccessors = new EdcStsAccountserviceLibraryAccessors(owner);
        private final EdcStsApiLibraryAccessors laccForEdcStsApiLibraryAccessors = new EdcStsApiLibraryAccessors(owner);
        private final EdcStsRemoteLibraryAccessors laccForEdcStsRemoteLibraryAccessors = new EdcStsRemoteLibraryAccessors(owner);

        public EdcStsLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>sts</b> with <b>org.eclipse.edc:identity-trust-sts-embedded</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.sts");
        }

        /**
         * Dependency provider for <b>core</b> with <b>org.eclipse.edc:identity-trust-sts-core</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getCore() {
            return create("edc.sts.core");
        }

        /**
         * Dependency provider for <b>spi</b> with <b>org.eclipse.edc:identity-trust-sts-spi</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getSpi() {
            return create("edc.sts.spi");
        }

        /**
         * Group of libraries at <b>edc.sts.accountservice</b>
         */
        public EdcStsAccountserviceLibraryAccessors getAccountservice() {
            return laccForEdcStsAccountserviceLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sts.api</b>
         */
        public EdcStsApiLibraryAccessors getApi() {
            return laccForEdcStsApiLibraryAccessors;
        }

        /**
         * Group of libraries at <b>edc.sts.remote</b>
         */
        public EdcStsRemoteLibraryAccessors getRemote() {
            return laccForEdcStsRemoteLibraryAccessors;
        }

    }

    public static class EdcStsAccountserviceLibraryAccessors extends SubDependencyFactory {

        public EdcStsAccountserviceLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>remote</b> with <b>org.eclipse.edc:sts-account-service-remote</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getRemote() {
            return create("edc.sts.accountservice.remote");
        }

    }

    public static class EdcStsApiLibraryAccessors extends SubDependencyFactory implements DependencyNotationSupplier {

        public EdcStsApiLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>org.eclipse.edc:identity-trust-sts-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> asProvider() {
            return create("edc.sts.api");
        }

        /**
         * Dependency provider for <b>accounts</b> with <b>org.eclipse.edc:identity-trust-sts-accounts-api</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getAccounts() {
            return create("edc.sts.api.accounts");
        }

    }

    public static class EdcStsRemoteLibraryAccessors extends SubDependencyFactory {

        public EdcStsRemoteLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>client</b> with <b>org.eclipse.edc:identity-trust-sts-remote-client</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getClient() {
            return create("edc.sts.remote.client");
        }

    }

    public static class EdcVaultLibraryAccessors extends SubDependencyFactory {

        public EdcVaultLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>hashicorp</b> with <b>org.eclipse.edc:vault-hashicorp</b> coordinates and
         * with version reference <b>edc</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getHashicorp() {
            return create("edc.vault.hashicorp");
        }

    }

    public static class JacksonLibraryAccessors extends SubDependencyFactory {
        private final JacksonDatatypeLibraryAccessors laccForJacksonDatatypeLibraryAccessors = new JacksonDatatypeLibraryAccessors(owner);

        public JacksonLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jackson.datatype</b>
         */
        public JacksonDatatypeLibraryAccessors getDatatype() {
            return laccForJacksonDatatypeLibraryAccessors;
        }

    }

    public static class JacksonDatatypeLibraryAccessors extends SubDependencyFactory {
        private final JacksonDatatypeJakartaLibraryAccessors laccForJacksonDatatypeJakartaLibraryAccessors = new JacksonDatatypeJakartaLibraryAccessors(owner);

        public JacksonDatatypeLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jackson.datatype.jakarta</b>
         */
        public JacksonDatatypeJakartaLibraryAccessors getJakarta() {
            return laccForJacksonDatatypeJakartaLibraryAccessors;
        }

    }

    public static class JacksonDatatypeJakartaLibraryAccessors extends SubDependencyFactory {

        public JacksonDatatypeJakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>jsonp</b> with <b>com.fasterxml.jackson.datatype:jackson-datatype-jakarta-jsonp</b> coordinates and
         * with version reference <b>jackson</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getJsonp() {
            return create("jackson.datatype.jakarta.jsonp");
        }

    }

    public static class JakartaLibraryAccessors extends SubDependencyFactory {
        private final JakartaJsonLibraryAccessors laccForJakartaJsonLibraryAccessors = new JakartaJsonLibraryAccessors(owner);

        public JakartaLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Group of libraries at <b>jakarta.json</b>
         */
        public JakartaJsonLibraryAccessors getJson() {
            return laccForJakartaJsonLibraryAccessors;
        }

    }

    public static class JakartaJsonLibraryAccessors extends SubDependencyFactory {

        public JakartaJsonLibraryAccessors(AbstractExternalDependencyFactory owner) { super(owner); }

        /**
         * Dependency provider for <b>api</b> with <b>jakarta.json:jakarta.json-api</b> coordinates and
         * with version reference <b>jakarta.json</b>
         * <p>
         * This dependency was declared in catalog libs.versions.toml
         */
        public Provider<MinimalExternalModuleDependency> getApi() {
            return create("jakarta.json.api");
        }

    }

    public static class VersionAccessors extends VersionFactory  {

        private final JakartaVersionAccessors vaccForJakartaVersionAccessors = new JakartaVersionAccessors(providers, config);
        public VersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>awaitility</b> with value <b>4.2.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getAwaitility() { return getVersion("awaitility"); }

        /**
         * Version alias <b>edc</b> with value <b>0.11.0-SNAPSHOT</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getEdc() { return getVersion("edc"); }

        /**
         * Version alias <b>jackson</b> with value <b>2.18.2</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJackson() { return getVersion("jackson"); }

        /**
         * Version alias <b>parsson</b> with value <b>1.1.6</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getParsson() { return getVersion("parsson"); }

        /**
         * Version alias <b>postgres</b> with value <b>42.7.3</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getPostgres() { return getVersion("postgres"); }

        /**
         * Version alias <b>restAssured</b> with value <b>5.5.0</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getRestAssured() { return getVersion("restAssured"); }

        /**
         * Group of versions at <b>versions.jakarta</b>
         */
        public JakartaVersionAccessors getJakarta() {
            return vaccForJakartaVersionAccessors;
        }

    }

    public static class JakartaVersionAccessors extends VersionFactory  {

        public JakartaVersionAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Version alias <b>jakarta.json</b> with value <b>2.1.3</b>
         * <p>
         * If the version is a rich version and cannot be represented as a
         * single version string, an empty string is returned.
         * <p>
         * This version was declared in catalog libs.versions.toml
         */
        public Provider<String> getJson() { return getVersion("jakarta.json"); }

    }

    public static class BundleAccessors extends BundleFactory {
        private final SqlBundleAccessors baccForSqlBundleAccessors = new SqlBundleAccessors(objects, providers, config, attributesFactory, capabilityNotationParser);

        public BundleAccessors(ObjectFactory objects, ProviderFactory providers, DefaultVersionCatalog config, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) { super(objects, providers, config, attributesFactory, capabilityNotationParser); }

        /**
         * Dependency bundle provider for <b>connector</b> which contains the following dependencies:
         * <ul>
         *    <li>org.eclipse.edc:boot</li>
         *    <li>org.eclipse.edc:connector-core</li>
         *    <li>org.eclipse.edc:http</li>
         *    <li>org.eclipse.edc:api-observability</li>
         *    <li>org.eclipse.edc:json-ld</li>
         *    <li>org.eclipse.edc:token-core</li>
         * </ul>
         * <p>
         * This bundle was declared in catalog libs.versions.toml
         */
        public Provider<ExternalModuleDependencyBundle> getConnector() {
            return createBundle("connector");
        }

        /**
         * Dependency bundle provider for <b>dcp</b> which contains the following dependencies:
         * <ul>
         *    <li>org.eclipse.edc:identity-trust-service</li>
         *    <li>org.eclipse.edc:identity-did-core</li>
         *    <li>org.eclipse.edc:identity-did-web</li>
         *    <li>org.eclipse.edc:oauth2-client</li>
         *    <li>org.eclipse.edc:identity-trust-core</li>
         * </ul>
         * <p>
         * This bundle was declared in catalog libs.versions.toml
         */
        public Provider<ExternalModuleDependencyBundle> getDcp() {
            return createBundle("dcp");
        }

        /**
         * Dependency bundle provider for <b>sts</b> which contains the following dependencies:
         * <ul>
         *    <li>org.eclipse.edc:identity-trust-sts-core</li>
         *    <li>org.eclipse.edc:identity-trust-sts-api</li>
         *    <li>org.eclipse.edc:identity-trust-sts-spi</li>
         *    <li>org.eclipse.edc:identity-trust-sts-embedded</li>
         * </ul>
         * <p>
         * This bundle was declared in catalog libs.versions.toml
         */
        public Provider<ExternalModuleDependencyBundle> getSts() {
            return createBundle("sts");
        }

        /**
         * Group of bundles at <b>bundles.sql</b>
         */
        public SqlBundleAccessors getSql() {
            return baccForSqlBundleAccessors;
        }

    }

    public static class SqlBundleAccessors extends BundleFactory {

        public SqlBundleAccessors(ObjectFactory objects, ProviderFactory providers, DefaultVersionCatalog config, ImmutableAttributesFactory attributesFactory, CapabilityNotationParser capabilityNotationParser) { super(objects, providers, config, attributesFactory, capabilityNotationParser); }

        /**
         * Dependency bundle provider for <b>sql.edc</b> which contains the following dependencies:
         * <ul>
         *    <li>org.eclipse.edc:asset-index-sql</li>
         *    <li>org.eclipse.edc:contract-definition-store-sql</li>
         *    <li>org.eclipse.edc:contract-negotiation-store-sql</li>
         *    <li>org.eclipse.edc:policy-definition-store-sql</li>
         *    <li>org.eclipse.edc:edr-index-sql</li>
         *    <li>org.eclipse.edc:transfer-process-store-sql</li>
         *    <li>org.eclipse.edc:data-plane-instance-store-sql</li>
         *    <li>org.eclipse.edc:sql-core</li>
         *    <li>org.eclipse.edc:sql-lease</li>
         *    <li>org.eclipse.edc:sql-pool-apache-commons</li>
         *    <li>org.eclipse.edc:transaction-local</li>
         *    <li>org.postgresql:postgresql</li>
         * </ul>
         * <p>
         * This bundle was declared in catalog libs.versions.toml
         */
        public Provider<ExternalModuleDependencyBundle> getEdc() {
            return createBundle("sql.edc");
        }

        /**
         * Dependency bundle provider for <b>sql.sts</b> which contains the following dependencies:
         * <ul>
         *    <li>org.eclipse.edc:sts-client-store-sql</li>
         *    <li>org.eclipse.edc:jti-validation-store-sql</li>
         *    <li>org.eclipse.edc:sql-core</li>
         *    <li>org.eclipse.edc:sql-pool-apache-commons</li>
         *    <li>org.eclipse.edc:transaction-local</li>
         *    <li>org.postgresql:postgresql</li>
         * </ul>
         * <p>
         * This bundle was declared in catalog libs.versions.toml
         */
        public Provider<ExternalModuleDependencyBundle> getSts() {
            return createBundle("sql.sts");
        }

    }

    public static class PluginAccessors extends PluginFactory {

        public PluginAccessors(ProviderFactory providers, DefaultVersionCatalog config) { super(providers, config); }

        /**
         * Plugin provider for <b>shadow</b> with plugin id <b>com.gradleup.shadow</b> and
         * with version <b>8.3.5</b>
         * <p>
         * This plugin was declared in catalog libs.versions.toml
         */
        public Provider<PluginDependency> getShadow() { return createPlugin("shadow"); }

    }

}

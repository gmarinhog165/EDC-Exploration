plugins {
    id("java")
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")

    // data source
    implementation("org.eclipse.edc:data-plane-spi:0.11.1")
    implementation("org.mongodb:mongodb-driver-sync:5.3.1")

    // cloud transfer
    implementation("org.eclipse.edc:control-plane-spi:0.11.1")

    implementation("org.eclipse.edc.aws:data-plane-aws-s3:0.11.1")
    implementation("org.eclipse.edc:validator-spi:0.11.1")

    // data sink
    implementation("org.eclipse.edc:boot-spi:0.11.1") // edc exception


}

tasks.test {
    useJUnitPlatform()
}
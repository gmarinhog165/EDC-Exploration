/*
 *  Copyright (c) 2020, 2021 Microsoft Corporation
 *
 *  This program and the accompanying materials are made available under the
 *  terms of the Apache License, Version 2.0 which is available at
 *  https://www.apache.org/licenses/LICENSE-2.0
 *
 *  SPDX-License-Identifier: Apache-2.0
 *
 *  Contributors:
 *       Microsoft Corporation - initial API and implementation
 *       Fraunhofer Institute for Software and Systems Engineering - added dependencies
 *       ZF Friedrichshafen AG - add dependency
 *
 */

plugins {
    `java-library`
}

dependencies {
    implementation(libs.edc.data.plane.spi)
    implementation("org.mongodb:mongodb-driver-sync:5.3.1")
    implementation("org.eclipse.edc.aws:validator-data-address-s3:0.11.1")
    implementation("org.eclipse.edc:control-plane-spi:0.11.1")
    implementation("org.eclipse.edc:boot-spi:0.11.1")
}

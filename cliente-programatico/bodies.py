def asset_body(file_name, container_name):
    return {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@type": "Asset",
        "properties": {
            "https://w3id.org/edc/v0.0.1/ns/id": file_name,
            "https://w3id.org/edc/v0.0.1/ns/datasetId": "SharedDataset",
            "https://w3id.org/edc/v0.0.1/ns/description": f"Asset for the blob {file_name}."
        },
        "dataAddress": {
            "@type": "DataAddress",
            "https://w3id.org/edc/v0.0.1/ns/type": "AzureStorage",
            "https://w3id.org/edc/v0.0.1/ns/blobName": file_name,
            "https://w3id.org/edc/v0.0.1/ns/container": container_name,
            "https://w3id.org/edc/v0.0.1/ns/account": "provider",
            "https://w3id.org/edc/v0.0.1/ns/keyName": "secretAccessKey"
        }
    }

def policy_body():
    return {
        "@context": {
            "@vocab": "https://w3id.org/edc/v0.0.1/ns/",
            "odrl": "http://www.w3.org/ns/odrl/2/"
        },
        "@id": "aPolicy",
        "policy": {
            "@context": "http://www.w3.org/ns/odrl.jsonld",
            "@type": "Set",
            "permission": [],
            "prohibition": [],
            "obligation": []
        }
    }

def contract_body(asset_id):
    return {
        "@context": {
            "@vocab": "https://w3id.org/edc/v0.0.1/ns/"
        },
        "@id": f"Contract_{asset_id}",
        "accessPolicyId": "aPolicy",
        "contractPolicyId": "aPolicy",
        "assetsSelector": [
            {
                "https://w3id.org/edc/v0.0.1/ns/operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                "https://w3id.org/edc/v0.0.1/ns/operator": "=",
                "https://w3id.org/edc/v0.0.1/ns/operandRight": asset_id
            }
        ]
    }

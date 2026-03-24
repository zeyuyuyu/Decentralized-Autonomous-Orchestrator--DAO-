import os
import yaml
from typing import Dict, List
from kubernetes import client, config

class DeploymentOrchestrator:
    def __init__(self, config_file: str = 'config.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        config.load_kube_config()
        self.api = client.AppsV1Api()

    def deploy_services(self, services: List[str]) -> None:
        for service in services:
            service_config = self.config['services'][service]
            self.create_deployment(service, service_config)
            self.create_service(service, service_config)

    def create_deployment(self, service: str, config: Dict) -> None:
        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(name=service),
            spec=client.V1DeploymentSpec(
                replicas=config['replicas'],
                selector=client.V1LabelSelector(
                    match_labels={'app': service}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={'app': service}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=service,
                                image=config['image'],
                                ports=[client.V1ContainerPort(container_port=config['port'])]
                            )
                        ]
                    )
                )
            )
        )
        self.api.create_namespaced_deployment(namespace='default', body=deployment)

    def create_service(self, service: str, config: Dict) -> None:
        service_obj = client.V1Service(
            metadata=client.V1ObjectMeta(name=service),
            spec=client.V1ServiceSpec(
                selector={'app': service},
                ports=[client.V1ServicePort(port=config['port'])]
            )
        )
        self.api.create_namespaced_service(namespace='default', body=service_obj)

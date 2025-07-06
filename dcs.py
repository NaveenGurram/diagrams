from diagrams import Cluster, Diagram, Edge
from diagrams.aws.database import DocumentDB
from diagrams.aws.network import ALB
from diagrams.onprem.network import Apache, Internet
from diagrams.programming.framework import Spring
from diagrams.programming.language import Java
from diagrams.aws.integration import SNS
from diagrams.aws.security import WAF

with Diagram("data-collection-architecture", show=True):
    internet = Internet("internet")
    cloudflare = WAF("cloudflare")

    with Cluster("AWS-VPC"):
        with Cluster("ExternalSubnet"):
            extLb = ALB("externalAlb")
            with Cluster("data-collection-ext-cluster \n \\(min=2, max=2 nodes\\)"):
                extApache = Apache("reverse-proxy")
                extLb >> Edge(label="443") >> extApache

        with Cluster("InternalSubnet"):
            intLb = ALB("internalAlb")
            with Cluster("data-collection-cluster \n \\(min=2, max=8 nodes\\)"):
                idGateway = Java("id-gateway")
                dcsApp = Spring("data-collection-app")
                intLb >> Edge(label="443") >> idGateway >> Edge(label="8080") >> dcsApp

            dcsApp >> DocumentDB("DocDb")
            dcsApp >> SNS("SNS")

    internet >> Edge(label="443") >> cloudflare >> Edge(label="443") >> extLb
    extApache >> Edge(label="443") >> intLb

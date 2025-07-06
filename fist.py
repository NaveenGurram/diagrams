from diagrams import Cluster, Diagram, Edge
from diagrams.aws.database import DocumentDB
from diagrams.aws.network import ALB
from diagrams.onprem.network import Apache, Internet
from diagrams.programming.framework import Spring
from diagrams.programming.language import Java
from diagrams.aws.integration import SQS
from diagrams.aws.security import WAF, Guardduty
from diagrams.aws.storage import S3

with Diagram("fist-architecture", show=True):
    internet = Internet("internet")
    cloudflare = WAF("cloudflare")

    with Cluster("AWS-VPC"):
        fistBucket = S3("fist-bucket")
        with Cluster("ExternalSubnet"):
            extLb = ALB("externalAlb")
            with Cluster("fist-ext-cluster \n \\(min=2, max=2 nodes\\)"):
                extApache = Apache("reverse-proxy")
                extLb >> Edge(label="443") >> extApache

        with Cluster("InternalSubnet"):
            intLb = ALB("internalAlb")
            with Cluster("fist-cluster \n \\(min=2, max=8 nodes\\)"):
                idGateway = Java("id-gateway")
                fistApp = Spring("fist-app")
                intLb >> Edge(label="443") >> idGateway >> Edge(label="8080") >> fistApp

            fistApp >> DocumentDB("DocDb")
            sqs = SQS("SQS")
            sqs >> Edge(label="check for virus scan") >> Guardduty("guard-duty") >> Edge(label="update object metadata") >> fistBucket
            fistBucket >> sqs >> Edge(label="read-s3-events") >> fistApp


    internet >> Edge(label="file upload") >> fistBucket
    internet >> Edge(label="443") >> cloudflare >> Edge(label="443") >> extLb
    extApache >> Edge(label="443") >> intLb
